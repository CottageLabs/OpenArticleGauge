import json, redis, logging

from openarticlegauge import config
from openarticlegauge.dao import DomainObject
from openarticlegauge.core import app
from openarticlegauge.slavedriver import celery

log = logging.getLogger(__name__)

class LookupException(Exception):
    def __init__(self, message):
        self.message = message
        super(LookupException, self).__init__(self, message)

class BufferException(Exception):
    def __init__(self, message):
        self.message = message
        super(BufferException, self).__init__(self, message)

class Record(DomainObject):
    __type__ = 'record'
    
    @classmethod
    def check_archive(cls, identifier):
        """
        Check the archive layer for an object with the given (canonical) identifier,
        which can be found in the bibjson['identifier']['canonical'] field
        
        Return a bibjson record
        """
        
        result = {}
        if config.BUFFERING:
            # before checking remote, check the buffer queue if one is enabled
            log.debug("checking buffer for " + str(identifier))
            result = cls._check_buffer(identifier)
            if result:
                log.debug(str(identifier) + " found in buffer")
            
        if not result:
            # by just making an ID and GETting and POSTing to it, we can do things faster.
            log.debug("checking remote archive for " + str(identifier))
            _id = identifier.replace('/','_')
            result = cls.pull(_id)
            if result:
                log.debug(str(identifier) + " found in remote archive")
            else:
                log.debug(str(identifier) + " did not yield a result in the archive")

        try:
            return result.data
        except:
            return result

    @classmethod
    def store(cls, bibjson):
        """
        Store the provided bibjson record in the archive (overwriting any item which
        has the same canonical identifier)
        """
        # normalise the canonical identifier for elastic search
        identifier = None # record this for logging
        for idobj in bibjson.get('identifier',[]):
            if 'canonical' in idobj.keys():
                bibjson['id'] = idobj['canonical'].replace('/','_')
                identifier = idobj['canonical']
        
        if config.BUFFERING:
            log.info("placing item " + identifier + " into the storage buffer")
            
            # just add to the buffer, no need to actually save anything
            cls._add_to_buffer(bibjson)
            return
        else:
            log.info("placing item " + identifier + " directly into storage")
            log.debug("saving bibjson: "+ str(bibjson))
            
            # no buffering, just save this one record
            r = cls(**bibjson)
            r.save()
    
    @classmethod
    def _add_to_buffer(cls, bibjson):
        canonical = None
        for identifier in bibjson.get("identifier", []):
            if "canonical" in identifier:
                canonical = identifier['canonical']
                break
        
        if canonical is None:
            raise BufferException("cannot buffer an item without a canonical form of the identifier")
        
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        s = json.dumps(bibjson)
        client.set("id_" + canonical, s)
    
    @classmethod
    def _check_buffer(cls, canonical):
        # query the redis cache for the bibjson record and return it
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        record = client.get("id_" + canonical)
        if record is None or record == "":
            return None
        return json.loads(record)
    
    @classmethod
    def flush_buffer(cls, key_timeout=0, block_size=1000):
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        
        # get all of the id keys
        ids = client.keys("id_*")
        if len(ids) == 0:
            log.info("storage buffer contains 0 items to be flushed ... returning")
            return False
        log.info("flushing storage buffer of " + str(len(ids)) + " objects")
        
        # retrieve all of the bibjson records associated with those keys
        
        bibjson_records = []
        i = 0
        for identifier in ids:
            # obtain, decode and register the bibjson record to be archived
            s = client.get(identifier)
            obj = json.loads(s)
            bibjson_records.append(obj)
            
            # if we've reached the block size, do a bulk write
            i += 1
            if i >= block_size:
                # bulk load the records
                cls.bulk(bibjson_records)
                
                # reset the registers
                i = 0
                bibjson_records = []
        
        if len(bibjson_records) > 0:
            # bulk load the remaining records
            cls.bulk(bibjson_records)
        
        # set a timeout on the identifiers affected, if desired.  If the key_timeout is 0, this is effectively
        # the same as deleting those keys
        for identifier in ids:
            client.expire(identifier, key_timeout)
        
        return True

class Issue(DomainObject):
    __type__ = 'issue'


class Log(DomainObject):
    __type__ = 'log'


class ResultSet(object):
    """
    {
	    "requested" : number_requested_in_batch,
	    "results" : [
		    the list of bibjson record objects already known
	    ],
	    "errors" : [
		    a list of JSON objects with an "identifier" key and an "error" key
	    ],
	    "processing" : [
		    a list of bibjson identifier objects that are on the queue
	    ]
    }
    """
    def __init__(self, bibjson_ids=[]):
        # FIXME: this is probably not the right way to initialise the object, or store
        # the internal state, but we can fix that later.  Important, first, just to make it work
        self.requested = len(bibjson_ids)
        self.results = []
        self.errors = []
        self.processing = []
        self.bibjson_ids = bibjson_ids
    
    def add_result_record(self, record):
        # get the bibjson if it exists
        bibjson = self._get_bibjson(record)
        
        # now find out if it is queued or if the bibjson record is None
        # and use this information to increment the counters
        if record.get("error") is not None:
            self.errors.append({"identifier" : record.get('identifier'), "error" : record.get("error")})
        elif record.get('queued', False) or bibjson is None:
            self.processing.append({"identifier" : record.get('identifier')})
        else:
            self.results.append(bibjson)
    
    def json(self):
        obj = {
            "requested" : self.requested,
            "results" :  self.results,
            "errors" :  self.errors,
            "processing" : self.processing
            }
        return json.dumps(obj)
    
    def _get_bibjson(self, record):
        # first get the bibjson record
        bibjson = record.get('bibjson')
        
        if bibjson is None:
            return None
        
        # ensure that the identifier is in the bibjson record
        # FIXME: this is pretty blunt, could be a lot smarter, and ultimately unnecessary anyway
        if not bibjson.has_key("identifier"):
            bibjson["identifier"] = []
        found = False
        for identifier in bibjson['identifier']:
            if identifier.has_key("canonical") and identifier['canonical'] == record['identifier']['canonical']:
                found = True
                break
        if not found:
            bibjson['identifier'].append(record['identifier'])
        
        return bibjson
        
@celery.task(name="openarticlegauge.models.flush_buffer")
def flush_buffer():
    # if we are not buffering, don't do anything
    if not config.BUFFERING:
        log.info("BUFFERING = False ; flush_buffer is superfluous, aborting")
        return False
    
    # check to see if we are already running a buffering process    
    client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
    lock = client.get("flush_buffer_lock")
    if lock is not None:
        log.warn("flush_buffer ran before previous iteration had completed - consider increasing the gaps between the run times for this scheduled task")
        return False
    
    # if we are not already running the buffering process, then carry on...
    
    # set a lock on this process, so that it doesn't run twice at the same time (see checks above)
    client.set("flush_buffer_lock", "lock")
    
    # call flush on the record objects that are buffered
    Record.flush_buffer(key_timeout=config.BUFFER_GRACE_PERIOD, block_size=config.BUFFER_BLOCK_SIZE)
    
    # set an expiry time on the lock, which is consistent with the expiry time applied to the 
    # buffered items.  This means this method will only run again once all the previously buffered
    # items have been removed from the buffer zone.
    client.expire("flush_buffer_lock", config.BUFFER_GRACE_PERIOD)
    
    # return true to indicate that the function ran
    return True
