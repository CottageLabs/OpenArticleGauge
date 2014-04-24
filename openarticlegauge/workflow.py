"""
Main processing business logic for the OAG application.  This is where the back-end processing
of requested identifiers actually happens, and where the asynchronous Celery tasks are defined
and triggered by requests.

Throughout this module we use the OAG record object as the message format that is passed around
the various functions.  Through the processing pipeline it is slowly fleshed out until it
reaches either completion or causes an error.  The record object in full is:

{
    "identifier" : {
        "id" : "<raw id provided by the client>",
        "type" : "<type of identifier, e.g doi or pmid>",
        "canonical" : "<canonical form of the identifier>"
    },
    "queued" : True/False,
    "provider" : {
        "url" : ["<provider url, e.g. dereferenced doi>", "..."],
        "doi" : "<provider doi>"
    },
    "bibjson" : {<bibjson object - see http://bibjson.org>}
}

The message object is represented by the models.MessageObject class, and all interactions
with this model should be via that class instance.

"""

from celery import chain
from openarticlegauge import models, config, cache, plugin
import logging
from openarticlegauge.slavedriver import celery

LOG_FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
log = logging.getLogger(__name__)

def lookup(bibjson_ids, priority=False):
    """
    Take a list of bibjson id objects
    {
        "id" : "<identifier>",
        "type" : "<type>"
    }
    and process them, returning a models.ResultSet object of completed or incomplete results
    
    arguments:
    bibjson_ids -- a list of bibjson id objects with optional type parameter
    priority -- should the request be placed on the priority queue
    
    returns:
    a models.ResultSet object with results, errors and a list of identifiers waiting to be processed
    
    """
    # FIXME: should we sanitise the inputs?
    
    # create a new resultset object
    log.debug("looking up ids: " + str(bibjson_ids))
    rs = models.ResultSet(bibjson_ids)
    
    # now run through each passed id, and either obtain a cached copy or 
    # inject it into the asynchronous back-end
    for bid in bibjson_ids:
        # first, create the basic record object
        record = models.MessageObject(bid=bid)
        log.debug("initial record " + str(record))
        
        # trap any lookup errors
        try:
            # Step 1: identifier type detection/verification
            _detect_verify_type(record)
            log.debug("type detected record " + str(record))
            
            # Step 1a: if we don't find a type for the identifier, there's no point in us continuing
            if record.identifier_type is None:
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
                if cached_copy.has_error():
                    raise models.LookupException("identifier has permanent errors - please contact us and let us know: " + cached_copy.error)
                if cached_copy.queued:
                    record.queued = True
                elif cached_copy.has_bibjson():
                    record.bibjson = cached_copy.bibjson
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
                record.bibjson = archived_bibjson
                log.debug("loaded from archive " + str(archived_bibjson))
                _update_cache(record)
                log.debug("archived item retrieved, so re-cache it " + str(record))
                rs.add_result_record(record)
                log.debug(str(bid) + " added to result, continuing ...")
                continue

            # Step 5: we need to check to see if any record we have has already
            # been queued.  In theory, this step is pointless, but we add it
            # in for completeness, and just in case any of the above checks change
            # in future
            if record.queued:
                # if the item is already queued, we just need to update the 
                # cache (which may be a null operation anyway), and then carry on
                # to the next record
                _update_cache(record)
                log.debug("caching record " + str(record))
                continue
                        
            # Step 6: if we get to here, we need to set the state of the record
            # queued, and then cache it.
            record.queued = True
            _update_cache(record)
            log.debug("caching record " + str(record))
            
            # Step 7: the record needs the licence looked up on it, so we inject
            # it into the asynchronous lookup workflow
            _start_back_end(record, priority)
            
        except models.LookupException as e:
            record.error = e.message
        
        # write the resulting record into the result set
        rs.add_result_record(record)
    
    # finish by returning the result set
    return rs

def _check_archive(record):
    """
    check the record archive for a copy of the bibjson record
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    - None if there is nothing for this record in the archive
    - a bibjson record if one is found
    
    """
    if record.canonical is None:
        raise models.LookupException("can't look anything up in the archive without a canonical id")
    
    # obtain a copy of the archived bibjson
    log.debug("checking archive for canonical identifier: " + record.canonical)
    archived_bibjson = models.Record.check_archive(record.canonical)
    
    # if it's not in the archive, return
    if archived_bibjson is None:
        # log.debug(record['identifier']['canonical'] + " is not in the archive")
        log.debug(record.canonical + " is not in the archive")
        return None
    
    # if there is archived bibjson, then we need to check whether it is stale
    # or not
    if _is_stale(models.MessageObject(bibjson=archived_bibjson)):
        # log.debug(record['identifier']['canonical'] + " is in the archive, but is stale")
        log.debug(record.canonical + " is in the archive, but is stale")
        return None
        
    # otherwise, just return the archived copy
    # log.debug(record['identifier']['canonical'] + " is in the archive")
    log.debug(record.canonical + " is in the archive")
    return archived_bibjson

def _update_cache(record):
    """
    update the cache, and reset the timeout on the cached item
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    """
    if record.canonical is None:
        raise models.LookupException("can't create/update anything in the cache without a canonical id")
    
    # update or create the cache
    # cache.cache(record['identifier']['canonical'], record)
    cache.cache(record.canonical, record)
    
def _invalidate_cache(record):
    """
    invalidate any cache object associated with the passed record
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    """
    if record.canonical is None:
        raise models.LookupException("can't invalidate anything in the cache without a canonical id")
    
    # cache.invalidate(record['identifier']['canonical'])
    cache.invalidate(record.canonical)

def _is_stale(record):
    """
    Do a stale check on the bibjson object.
    
    arguments:
    record -- the bibjson record to carry out the stale check on
    
    """
    # return cache.is_stale(bibjson)
    return cache.is_stale(record)

def _check_cache(record):
    """
    check the live local cache for a copy of the object.  Whatever we find,
    return it (a record of a queued item, a full item, or None)
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    - None if nothing in the cache or the cached record is found to be stale
    - OAG record object if one is found
    
    """
    if record.canonical is None:
        raise models.LookupException("can't look anything up in the cache without a canonical id")
    
    log.debug("checking cache for key: " + record.canonical)
    cached_copy = cache.check_cache(record.canonical)
    
    # if it's not in the cache, then return
    if cached_copy is None:
        log.debug(record.canonical + " not found in cache")
        return None
        
    # if the cached copy exists ...
        
    # first check to see if the cached copy is already on the queue
    if cached_copy.queued:
        log.debug(record.canonical + " is in the cache and is queued for processing")
        return cached_copy
    
    # next check to see if this is a record of an error
    if cached_copy.has_error():
        log.debug(record.canonical + " is in the cache, and has a permanent error attached to it")
        return cached_copy
    
    # next check to see if the cached copy has a bibjson record in it
    if cached_copy.has_bibjson():
        # if it does, we need to see if the record is stale.  If so, we remember that fact,
        # and we'll deal with updating stale items later (once we've checked bibserver)
        if _is_stale(cached_copy):
            log.debug(record.canonical + " is in the cache but is a stale record")
            _invalidate_cache(record)
            return None
    
    # otherwise, just return the cached copy
    # log.debug(record['identifier']['canonical'] + " is in the cache")
    log.debug(record.canonical + " is in the cache")
    return cached_copy

def _canonicalise_identifier(record):
    """
    load the appropriate plugin to canonicalise the identifier.  This will add a "canonical" field
    to the "identifier" record with the canonical form of the identifier to be used in cache control and bibserver
    lookups
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    """
    # verify that we have everything required for this step
    if not record.has_id() or not record.has_type():
        raise models.LookupException("bibjson identifier object does not contain a 'type' and/or 'id' field")
    
    # load the relevant plugin based on the "type" field, and then run it on the record object
    # p = plugin.PluginFactory.canonicalise(record['identifier']['type'])
    p = plugin.PluginFactory.canonicalise(record.identifier_type)
    if p is None:
        # raise models.LookupException("no plugin for canonicalising " + record['identifier']['type'])
        raise models.LookupException("no plugin for canonicalising " + record.identifier_type)
    # p.canonicalise(record['identifier'])
    p.canonicalise(record)

def _detect_verify_type(record):
    """
    run through a set of plugins which will detect the type of id, and verify that it meets requirements
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    """
    # verify that the record has an identifier key, which is required for this operation
    #if not record.has_key("identifier"):
    #    raise models.LookupException("no identifier in record object")
    
    #if not record['identifier'].has_key("id"):
    if not record.has_id():
        raise models.LookupException("bibjson identifier object does not contain an 'id' field")
    
    # run through /all/ of the plugins and give each a chance to augment/check
    # the identifier
    plugins = plugin.PluginFactory.type_detect_verify()
    for p in plugins:
        # p.type_detect_verify(record['identifier'])
        p.type_detect_verify(record)
    
def _start_back_end(record, priority=False):
    """
    kick off the asynchronous licence lookup process.  There is no need for this to return
    anything, although a handle on the asynchronous request object is provided for convenience of
    testing
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    AsyncRequest object from the Celery framework
    
    """
    log.debug("injecting record into asynchronous processing chain: " + str(record))
    
    # ask the record to prep itself for injection into the processing chain
    # this will return just the record dictionary (not the message object), and will
    # have removed the existing journal information and added any processing flags 
    # that are relevant
    chainable = record.prep_for_backend() 
    log.debug("record prepped for chain: " + str(chainable))
    
    if priority:
        ch = chain(priority_detect_provider.s(chainable), priority_provider_licence.s(), priority_store_results.s())
        r = ch.apply_async()
        return r
    else:
        ch = chain(detect_provider.s(chainable), provider_licence.s(), store_results.s())
        r = ch.apply_async()
        return r

############################################################################
# Celery Tasks
############################################################################    

@celery.task(name="openarticlegauge.workflow.detect_provider")
def detect_provider(record_json):
    return do_detect_provider(record_json)

@celery.task(name="openarticlegauge.workflow.priority_detect_provider")
def priority_detect_provider(record_json):
    return do_detect_provider(record_json)

def do_detect_provider(record_json):
    """
    Attempt to detect the provider of the identifier supplied in the record.  This
    will - if successful - add the record['provider'] object to the OAG record
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    the passed in record with the 'provider' field added if possible
    
    """
    try:
        record = models.MessageObject(record=record_json)
    except Exception as e:
        error = "Unable to parse record_json into MessageObject in detect_provider: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in detect_provider: " + error)
            return record_json
        except:
            return {"error" : error}
        
    try:
        # Step 1: see if we can actually detect a provider at all?
        # as usual, this should never happen, but we should have a way to 
        # handle it
        if record.identifier_type is None:
            record.error = "No identifier type detected, so no provider detectable"
            return record.record
        
        # Step 2: get the provider plugins that are relevant, and
        # apply each one until a provider string is added
        plugins = plugin.PluginFactory.detect_provider(record.identifier_type)
        for p in plugins:
            log.debug("applying plugin " + str(p._short_name))
            p.detect_provider(record)
        
        # we have to return the record, so that the next step in the chain
        # can deal with it
        log.debug("yielded result " + str(record))
        return record.record
        
    except Exception as e:
        error = "Irretrievable error in detect_provider: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in detect_provider: " + error)
            return record_json
        except:
            return {"error" : error}
    
@celery.task(name="openarticlegauge.workflow.provider_licence")
def provider_licence(record_json):
    return do_provider_licence(record_json)

@celery.task(name="openarticlegauge.workflow.priority_provider_licence")
def priority_provider_licence(record_json):
    return do_provider_licence(record_json)

def do_provider_licence(record_json):
    """
    Attempt to determine the licence of the record based on the provider information
    contained in record['provider'].  Whether this is successful or not a record['bibjson']['license']
    record will be added.  If the operation was successful this will contain a licence
    statement about the item conforming to the OAG record specification.  If the operation was
    not successful it will contain a "failed-to-obtain-license" record, indicating the
    terms of the failure.
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    the passed in record object with the record['bibjson']['license'] field added or appended to with
        a new licence
    
    """
    try:
        record = models.MessageObject(record=record_json)
    except Exception as e:
        error = "Unable to parse record_json into MessageObject in provider_licence: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in provider_licence: " + error)
            return record_json
        except:
            return {"error" : error}
    
    try:
        # Step 1: check that we have a provider indicator to work from
        if not record.has_provider():
            log.debug("record has no provider, so unable to look for licence: " + str(record))
            record.error = "Record has no provider, so unable to look for licence"
            return record.record
        
        # Step 2: get the plugin that will run for the given provider
        p = plugin.PluginFactory.license_detect(record.provider)
        if p is None:
            log.debug("No plugin to handle provider: " + str(record.provider))
            record.error = "No plugin to handle provider"
            return record.record
        
        # Step 3: run the plugin on the record
        log.debug("Plugin " + str(p) + " to handle provider " + str(record.provider))
        p.license_detect(record)
        
        # was the plugin able to detect a licence?
        # if not, we need to add an unknown licence for this provider
        if not record.has_license() and not record.was_licensed():
            log.debug("No licence detected by plugin " + p._short_name + " so adding unknown licence")
            record.add_license(
                url=config.unknown_url,
                type="failed-to-obtain-license",
                open_access=False,
                error_message="unable to detect licence",
                category="failure",
                provenance_description="a plugin ran and failed to detect a license for this record.  This entry records that the license is therefore unknown",
                handler=p._short_name,
                handler_version=p.__version__
            )
        elif not record.has_license() and record.was_licensed():
            log.debug("No license detected by plugin " + p._short_name + " but was previously licensed, so NOT adding unknown license")

        # we have to return the record so that the next step in the chain can
        # deal with it
        log.debug("plugin " + str(p) + " yielded result " + str(record))
        return record.record
        
    except Exception as e:
        error = "Irretrievable error in provider_licence: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in provider_licence: " + error)
            return record_json
        except:
            return {"error" : error}

@celery.task(name="openarticlegauge.workflow.store_results")
def store_results(record_json):
    return do_store_results(record_json)

@celery.task(name="openarticlegauge.workflow.priority_store_results")
def priority_store_results(record_json):
    return do_store_results(record_json)

def do_store_results(record_json):
    """
    Store the OAG record object in all the appropriate locations:
    - in the cache
    - in the archive
    
    In order to achieve this, this method will also ensure that the object
    has at least one licence (indicating that we "failed-to-obtain-license"), and
    that the bibjson identifiers are all in the appropriate locations.  
    
    It will then remove the item from the processing queue prior to storage
    
    arguments:
    record -- an OAG record object, see the module documentation for details
    
    returns:
    passed in record object, with the queued status removed and any other internal changes
        necessary to prepare it for storage
    
    """
    try:
        record = models.MessageObject(record=record_json)
    except Exception as e:
        error = "Unable to parse record_json into MessageObject in store_results: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in store_results: " + error)
            # note that we do not return in this instance - we will still try to record this incident in the cache below
        except:
            return {"error" : error}
    
    try:
        # Step 0: ensure that the record has an identifier
        # This is the only occasion where we can't store a record of the error, but if it
        # occurs, we are in big trouble code-wise anyway!
        if record.canonical is None:
            record.error = "No canonical identifier at the end of the chain, so unable to store"
            return record.record
    
        # Step 1: ensure that a licence was applied, and if not apply one
        if not record.has_bibjson():
            # no bibjson record, so add a blank one
            log.debug("record does not have a bibjson record.")
            record.bibjson = {}
            
        if not record.has_license() and not record.was_licensed():
            # the bibjson record does not contain a license list OR the license list is of zero length
            log.debug("Licence could not be detected, therefore adding 'unknown' licence to " + str(record.bibjson))
            record.add_license(
                url=config.unknown_url,
                type="failed-to-obtain-license",
                open_access=False,
                error_message="unable to detect licence",
                category="failure",
                provenance_description="no plugin was found that would try to detect a licence.  This entry records that the license is therefore unknown",
                handler="oag",
                handler_version="0.0" # we provide a placeholder handler, so that we can discover and invalidate it later
            )
        elif not record.has_license() and record.was_licensed():
            log.debug("Licence could not be detected, but was previously licensed, so NOT adding unknown license")
            
        # Step 2: unqueue the record
        if record.queued:
            log.debug(str(record.identifier) + ": removing this item from the queue")
            record.queued = False
        
        # Step 2.5: determine if this is already in the archive
        existing_bibjson = _check_archive(record)
        if existing_bibjson is not None:
            # if already archived, then we need to merge the existing licenses with the newly
            # discovered licenses
            log.debug(str(record.identifier) + ": has record in archive; merging")
            record.merge(existing_bibjson)
        
        # Step 3: update the archive if no errors
        record.add_identifier_to_bibjson()
        if not record.has_error():
            log.debug(str(record.identifier) + ": storing this item in the archive")
            models.Record.store(record.bibjson)
        else:
            # otherwise, record the error in the error index
            log.debug(str(record.identifier) + ": experienced an error in the chain - not storing in the archive")
            err = models.Error(**record.record)
            err.save()
        
        # Step 4: update the cache
        log.debug(str(record.identifier) + ": storing this item in the cache")
        _update_cache(record)
        
        # we have to return the record so that the next step in the chain can
        # deal with it (if such a step exists)
        log.debug("yielded result " + str(record))
        return record.record
        
    except Exception as e:
        # if we find ourselves here, there's not a lot we can do - just fail
        error = "Irretrievable error in store_results: " + e.message
        try:
            record_json["error"] = error
            log.debug("error in store_results: " + error)
            return record_json
        except:
            return {"error" : error}

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
