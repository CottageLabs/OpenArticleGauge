from celery import chain
from isitopenaccess import models, config, cache, plugin, recordmanager
import logging
from slavedriver import celery

#logging.basicConfig(filename='iioa.log',level=logging.DEBUG)
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
    log.debug("looking up ids: " + str(bibjson_ids))
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
            
            # Step 1a: if we don't find a type for the identifier, there's no point in us continuing
            if record.get("identifier", {}).get("type") is None:
                raise models.LookupException("unable to determine the type of the identifier")
            
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
                log.debug(str(bid) + " added to result, continuing ...")
                continue
            
            # Step 4: check the archive for an existing record
            archived_bibjson = _check_archive(record)
            log.debug("archived bibjson: " + str(archived_bibjson))
            
            # this returns either a valid, returnable copy of the record, or None
            # if the record is not archived, or is stale
            if archived_bibjson is not None:
                record['bibjson'] = archived_bibjson
                log.debug("loaded from archive " + str(archived_bibjson))
                rs.add_result_record(record)
                continue

            # Step 5: we need to check to see if any record we have has already
            # been queued.  In theory, this step is pointless, but we add it
            # in for completeness, and just in case any of the above checks change
            # in future
            if record.get("queued", False):
                # if the item is already queued, we just need to update the 
                # cache (which may be a null operation anyway), and then carry on
                # to the next record
                _update_cache(record)
                log.debug("caching record " + str(record))
                continue
                        
            # Step 6: if we get to here, we need to set the state of the record
            # queued, and then cache it.
            record['queued'] = True
            _update_cache(record)
            log.debug("caching record " + str(record))
            
            # Step 7: the record needs the licence looked up on it, so we inject
            # it into the asynchronous lookup workflow
            _start_back_end(record)
            
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
    log.debug("checking archive for canonical identifier: " + record['identifier']['canonical'])
    archived_bibjson = models.Record.check_archive(record['identifier']['canonical'])
    
    # if it's not in the archive, return
    if archived_bibjson is None:
        log.debug(record['identifier']['canonical'] + " is not in the archive")
        return None
    
    # if there is archived bibjson, then we need to check whether it is stale
    # or not
    if _is_stale(archived_bibjson):
        log.debug(record['identifier']['canonical'] + " is in the archive, but is stale")
        return None
        
    # otherwise, just return the archived copy
    log.debug(record['identifier']['canonical'] + " is in the archive")
    return archived_bibjson

def _update_cache(record):
    """
    update the cache, and reset the timeout on the cached item
    """
    if not record.has_key('identifier'):
        raise models.LookupException("no identifier in record object")
    
    if not record['identifier'].has_key('canonical'):
        raise models.LookupException("can't create/update anything in the cache without a canonical id")
    
    # update or create the cache
    cache.cache(record['identifier']['canonical'], record)
    
def _invalidate_cache(record):
    """
    invalidate any cache object associated with the passed record
    """
    if not record.has_key('identifier'):
        raise models.LookupException("no identifier in record object")
    
    if not record['identifier'].has_key('canonical'):
        raise models.LookupException("can't invalidate anything in the cache without a canonical id")
    
    cache.invalidate(record['identifier']['canonical'])

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
    
    log.debug("checking cache for key: " + record['identifier']['canonical'])
    cached_copy = cache.check_cache(record['identifier']['canonical'])
    
    # if it's not in the cache, then return
    if cached_copy is None:
        log.debug(record['identifier']['canonical'] + " not found in cache")
        return None
        
    # if the cached copy exists ...
        
    # first check to see if the cached copy is already on the queue
    if cached_copy.get('queued', False):
        log.debug(record['identifier']['canonical'] + " is in the cache and is queued for processing")
        return cached_copy
    
    # next check to see if the cached copy has a bibjson record in it
    if cached_copy.has_key('bibjson'):
        # if it does, we need to see if the record is stale.  If so, we remember that fact,
        # and we'll deal with updating stale items later (once we've checked bibserver)
        if _is_stale(cached_copy['bibjson']):
            log.debug(record['identifier']['canonical'] + " is in the cache but is a stale record")
            _invalidate_cache(record)
            return None
    
    # otherwise, just return the cached copy
    log.debug(record['identifier']['canonical'] + " is in the cache")
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
    p = plugin.PluginFactory.canonicalise(record['identifier']['type'])
    if p is None:
        raise models.LookupException("no plugin for canonicalising " + record['identifier']['type'])
    p.canonicalise(record['identifier'])

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
    plugins = plugin.PluginFactory.type_detect_verify()
    for p in plugins:
        p.type_detect_verify(record['identifier'])
    
def _start_back_end(record):
    """
    kick off the asynchronous licence lookup process.  There is no need for this to return
    anything, although a handle on the asynchronous is provided for convenience of
    testing
    """
    ch = chain(detect_provider.s(record), provider_licence.s(), store_results.s())
    r = ch.apply_async()
    return r

############################################################################
# Celery Tasks
############################################################################    

@celery.task(name="isitopenaccess.workflow.detect_provider")
def detect_provider(record):
    # Step 1: see if we can actually detect a provider at all?
    # as usual, this should never happen, but we should have a way to 
    # handle it
    if not record.has_key("identifier"):
        return record
    
    if not record['identifier'].has_key("type"):
        return record
    
    # Step 2: get the provider plugins that are relevant, and
    # apply each one until a provider string is added
    plugins = plugin.PluginFactory.detect_provider(record['identifier']["type"])
    for p in plugins:
        log.debug("applying plugin " + str(p._short_name))
        p.detect_provider(record)
    
    # we have to return the record, so that the next step in the chain
    # can deal with it
    log.debug("yielded result " + str(record))
    return record
    
@celery.task(name="isitopenaccess.workflow.provider_licence")
def provider_licence(record):
    # Step 1: check that we have a provider indicator to work from
    if not record.has_key("provider"):
        log.debug("record has no provider, so unable to look for licence: " + str(record))
        return record
    
    # Step 2: get the plugin that will run for the given provider
    p = plugin.PluginFactory.license_detect(record["provider"])
    if p is None:
        log.debug("No plugin to handle provider: " + str(record['provider']))
        return record
    log.debug("Plugin " + str(p) + " to handle provider " + str(record['provider']))
    
    # Step 3: run the plugin on the record
    if "bibjson" not in record:
        # if the record doesn't have a bibjson element, add a blank one
        record['bibjson'] = {}
    p.license_detect(record)
    
    # was the plugin able to detect a licence?
    # if not, we need to add an unknown licence for this provider
    if "license" not in record['bibjson'] or len(record['bibjson'].get("license", [])) == 0:
        log.debug("No licence detected by plugin " + p._short_name + " so adding unknown licence")
        recordmanager.add_license(record, 
            url=config.unknown_url,
            type="failed-to-obtain-license",
            open_access=False,
            error_message="unable to detect licence",
            category="failure",
            provenance_description="a plugin ran and failed to detect a license for this record.  This entry records that the license is therefore unknown",
            handler=p._short_name,
            handler_version=p.__version__
        )
        # describe_license_fail(record, "none", "unable to detect licence", "", config.unknown_url, p._short_name, p.__version__)

    # we have to return the record so that the next step in the chain can
    # deal with it
    log.debug("plugin " + str(p) + " yielded result " + str(record))
    return record

@celery.task(name="isitopenaccess.workflow.store_results")
def store_results(record):
    # Step 1: ensure that a licence was applied, and if not apply one
    if "bibjson" not in record:
        # no bibjson record, so add a blank one
        log.debug("record does not have a bibjson record.")
        record['bibjson'] = {}
        
    if "license" not in record['bibjson'] or len(record['bibjson'].get("license", [])) == 0:
        # the bibjson record does not contain a license list OR the license list is of zero length
        log.debug("Licence could not be detected, therefore adding 'unknown' licence to " + str(record['bibjson']))
        recordmanager.add_license(record,
            url=config.unknown_url,
            type="failed-to-obtain-license",
            open_access=False,
            error_message="unable to detect licence",
            category="failure",
            provenance_description="no plugin was found that would try to detect a licence.  This entry records that the license is therefore unknown",
        )
        # describe_license_fail(record, "none", "unable to detect licence", "", config.unknown_url)
        
    # Step 2: unqueue the record
    if record.has_key("queued"):
        log.debug(str(record['identifier']) + ": removing this item from the queue")
        del record["queued"]
    
    # Step 3: update the archive
    _add_identifier_to_bibjson(record['identifier'], record['bibjson'])
    log.debug(str(record['identifier']) + ": storing this item in the archive")
    models.Record.store(record['bibjson'])
    
    # Step 4: update the cache
    log.debug(str(record['identifier']) + ": storing this item in the cache")
    _update_cache(record)
    
    # we have to return the record so that the next step in the chain can
    # deal with it (if such a step exists)
    log.debug("yielded result " + str(record))
    return record

def _add_identifier_to_bibjson(identifier, bibjson):
    # FIXME: this is pretty blunt, could be a lot smarter
    if not bibjson.has_key("identifier"):
        bibjson["identifier"] = []
    found = False
    for identifier in bibjson['identifier']:
        if identifier.has_key("canonical") and identifier['canonical'] == bibjson['identifier']['canonical']:
            found = True
            break
    if not found:
        bibjson['identifier'].append(identifier)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
