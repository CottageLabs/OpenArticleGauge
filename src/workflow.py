from celery import chain
from slavedriver.workers import detect_provider, provider_site_plugins, provider_page_plugins
import models, config, cache, archive
import logging

log = logging.getLogger(__name__)

def lookup(bibjson_ids):
    """
    Take a list of bibjson id objects
    {
        "id" : "<identifier>",
        "type" : "<type>"
    }
    and process them, returning a models.ResultSet object of completed or incomplete results
    """
    # FIXME: should we sanitise the inputs?
    
    # create a new resultset object
    rs = models.ResultSet(bibjson_ids)
    
    # now run through each passed id, and either obtain a cached copy or 
    # inject it into the asynchronous back-end
    for bid in bibjson_ids:
        # first, create the basic record object
        record = { "identifier" : bid }
        log.debug("initial record " + str(record))
        
        # trap any lookup errors
        try:
            # Step 1: identifier type detection/verification
            _detect_verify_type(record)
            log.debug("type detected record " + str(record))
            
            # Step 2: create a canonical version of the identifier for cache keying
            _canonicalise_identifier(record)
            log.debug("canonicalised record " + str(record))
            
            # Step 3: check the cache for an existing record
            cached_copy = _check_cache(record)
            log.debug("cached record " + str(cached_copy))
            
            # this returns either a valid, returnable copy of the record, or None
            # if the record is not cached or is stale
            if cached_copy is not None:
                if cached_copy.get('queued', False):
                    record['queued'] = True
                elif cached_copy.has_key('bibjson'):
                    record['bibjson'] = cached_copy['bibjson']
                log.debug("loaded from cache " + str(record))
                rs.add_result_record(record)
                continue
            
            # Step 4: check the archive for an existing record
            archived_bibjson = _check_archive(record)
            log.debug("archived bibjson: " + str(archived_bibjson))
            
            # this returns either a valid, returnable copy of the record, or None
            # if the record is not archived, or is stale
            if archived_bibjson is not None:
                record['bibjson'] = archived_bibjson
                rs.add_result_record(record)
                continue
            
        except models.LookupException as e:
            record['error'] = e.message
        
        # write the resulting record into the result set
        rs.add_result_record(record)
    
    # finish by returning the result set
    return rs

def _check_archive(record):
    """
    check the record archive for a copy of the bibjson record
    """
    if not record.has_key('identifier'):
        raise models.LookupException("no identifier in record object")
        
    if not record['identifier'].has_key('canonical'):
        raise models.LookupException("can't look anything up in the archive without a canonical id")
        
    # obtain a copy of the archived bibjson
    archived_bibjson = archive.check_archive(record['identifier']['canonical'])
    
    # if it's not in the archive, return
    if archived_bibjson is None:
        return None
    
    # if there is archived bibjson, then we need to check whether it is stale
    # or not
    if _is_stale(archived_bibjson):
        return None
        
    # otherwise, just return the archived copy
    return archived_bibjson

def _invalidate_cache(record):
    """
    invalidate any cache object associated with the passed record
    """
    if not record.has_key('canonical'):
        raise models.LookupException("can't look anything up in the cache without a canonical id")
    
    cache.invalidate(record['canonical'])

def _is_stale(bibjson):
    """
    Do a stale check on the bibjson object.
    """
    return cache.is_stale(bibjson)

def _check_cache(record):
    """
    check the live local cache for a copy of the object.  Whatever we find,
    return it (a record of a queued item, a full item, or None)
    """
    if not record.has_key('identifier'):
        raise models.LookupException("no identifier in record object")
        
    if not record['identifier'].has_key('canonical'):
        raise models.LookupException("can't look anything up in the cache without a canonical id")
    
    cached_copy = cache.check_cache(record['identifier']['canonical'])
    
    # if it's not in the cache, then return
    if cached_copy is None:
        return None
        
    # if the cached copy exists ...
        
    # first check to see if the cached copy is already on the queue
    if cached_copy.get('queued', False):
        return cached_copy
    
    # next check to see if the cached copy has a bibjson record in it
    if cached_copy.has_key('bibjson'):
        # if it does, we need to see if the record is stale.  If so, we remember that fact,
        # and we'll deal with updating stale items later (once we've checked bibserver)
        if _is_stale(cached_copy['bibjson']):
            _invalidate_cache(record)
            return None
    
    # otherwise, just return the cached copy
    return cached_copy

def _canonicalise_identifier(record):
    """
    load the appropriate plugin to canonicalise the identifier.  This will add a "canonical" field
    to the "identifier" record with the canonical form of the identifier to be used in cache control and bibserver
    lookups
    """
    # verify that we have everything required for this step
    if not record.has_key("identifier"):
        raise models.LookupException("no identifier in record object")
    
    if not record['identifier'].has_key("id"):
        raise models.LookupException("bibjson identifier object does not contain an 'id' field")
        
    if not record['identifier'].has_key("type"):
        raise models.LookupException("bibjson identifier object does not contain a 'type' field")
    
    # load the relevant plugin based on the "type" field, and then run it on the record object
    plugin = config.canonicalisers.get(record['identifier']['type'])
    if plugin is None:
        raise models.LookupException("no plugin for canonicalising " + record['identifier']['type'])
    plugin(record)

def _detect_verify_type(record):
    """
    run through a set of plugins which will detect the type of id, and verify that it meets requirements
    """
    # verify that the record has an identifier key, which is required for this operation
    if not record.has_key("identifier"):
        raise models.LookupException("no identifier in record object")
    
    if not record['identifier'].has_key("id"):
        raise models.LookupException("bibjson identifier object does not contain an 'id' field")
    
    # run through /all/ of the plugins and give each a chance to augment/check
    # the identifier
    for plugin in config.type_detection:
        plugin(record["identifier"])
    

def start_back_end(record):
    ch = chain(detect_provider.s(record), provider_site_plugins.s(), provider_page_plugins.s())
    r = ch.apply_async()
    return r
