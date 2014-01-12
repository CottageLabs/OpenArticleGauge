"""
Data model objects, some of which extend the DAO for storage purposes

"""

import json, redis, logging

from openarticlegauge import config
from openarticlegauge.dao import DomainObject
from openarticlegauge.core import app
from openarticlegauge.slavedriver import celery

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

log = logging.getLogger(__name__)

class LookupException(Exception):
    """
    Exception to be thrown when there is a problem looking up a record
    
    """
    def __init__(self, message):
        self.message = message
        super(LookupException, self).__init__(self, message)

class BufferException(Exception):
    """
    Exception to be thrown when there is a problem with the storage buffer
    
    """
    def __init__(self, message):
        self.message = message
        super(BufferException, self).__init__(self, message)

class Account(DomainObject, UserMixin):
    __type__ = 'account'

    @classmethod
    def pull_by_email(cls, email):
        res = cls.query(q='email:"' + email + '"')
        if res.get('hits',{}).get('total',0) == 1:
            return cls(**res['hits']['hits'][0]['_source'])
        else:
            return None

    def set_password(self, password):
        self.data['password'] = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.data['password'], password)

    @property
    def email(self):
        return self.data.get("email")

    @property
    def is_super(self):
        #return not self.is_anonymous() and self.id in app.config.get('SUPER_USER', [])
        return False

class Record(DomainObject):
    __type__ = 'record'
    
    @classmethod
    def check_archive(cls, identifier):
        """
        Check the archive layer for an object with the given (canonical) identifier,
        which can be found in the bibjson['identifier']['canonical'] field
        
        arguments:
        identifier -- the identifier of the record to look up.  This should be the canonical identifier of the record
        
        Return a bibjson record or None if none is found
        
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
        has the same canonical identifier).  Depending on the configuration, this method
        may put the item into a buffer to be written out to storage at some later time
        in the future.
        
        arguments:
        bibjson -- the bibjson record to be stored.  The record must contain a canonical identifier in ['identifier'][n]['canonical']
        
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
        """
        add the given bibjson record to the storage buffer
        
        arguments:
        bibjson -- the bibjson record to be stored.  The record must contain a canonical identifier in ['identifier'][n]['canonical']
        
        """
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
        """
        Check the storage buffer for an item identified by the supplied canonical identifier
        
        arguments:
        identifier -- the identifier of the record to look up.  This should be the canonical identifier of the record
        
        Return a bibjson record or None if none is found
        
        """
        # query the redis cache for the bibjson record and return it
        client = redis.StrictRedis(host=config.REDIS_BUFFER_HOST, port=config.REDIS_BUFFER_PORT, db=config.REDIS_BUFFER_DB)
        record = client.get("id_" + canonical)
        if record is None or record == "":
            return None
        return json.loads(record)
    
    @classmethod
    def flush_buffer(cls, key_timeout=0, block_size=1000):
        """
        Flush the current storage buffer out to the long-term storage (Elasticsearch).  This method
        will return after all of the records have been flushed successfully to storage, and will
        not wait until the key_timeout period has passed (this will happen asynchronously)
        
        keyword arguments:
        key_timeout -- the length of time to live (in seconds) to allocate to each record in the storage buffer.  This is to 
            allow Elasticsearch time to receive and index the records and make them available - while it is
            doing that, the records will remain available in the storage buffer
            
        block_size -- maximum size of the list of records to send to the long-term storage in one HTTP request.
            if there are more records than the block size, multiple HTTP requests will be made, none of which
            will be larger than the block_size.
        
        returns:
        False if there is nothing in the buffer to flush
        True if there are items in the buffer to flush and they are successfully flushed
        
        """
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


class License(DomainObject):
    __type__ = 'license'


class ResultSet(object):
    """
    Model object to represent the return object from the API.  It represents the following data structure:
    
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
        """
        Construct a new ResultSet object around the list of bibjson_ids supplied to the API
        
        arguments
        bibjson_ids -- list of bibjson identifier objects
        
        """
        self.requested = len(bibjson_ids)
        self.results = []
        self.errors = []
        self.processing = []
        self.bibjson_ids = bibjson_ids
    
    def add_result_record(self, record):
        """
        Add the given record to the result set.  This will inspect the content of the record and
        add it to the appropriate part of the response
        
        arguments
        record -- OAG record object.  See the high level documentation for details on its structure
        
        """
        
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
        """
        Get a JSON representation of this object
        
        returns a JSON serialisation of the object
        
        """
        
        obj = {
            "requested" : self.requested,
            "results" :  self.results,
            "errors" :  self.errors,
            "processing" : self.processing
            }
        return json.dumps(obj)
    
    def _get_bibjson(self, record):
        """
        Get the bibjson from the supplied record.  This involves finding the bibjson
        record in record['bibjson'] and reconciling this with any identifiers in record['identifier']
        to ensure that all relevant identifiers are represented.
        
        arguments:
        record -- OAG record object.  See the high level documentation for details on its structure
        
        """
        
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
    """
    Celery task for flushing the storage buffer.  This should be promoted onto a
    processing queue by Celery Beat (see the celeryconfig).  This will process will
    lock the buffer so that parallel execution is not possible.
    
    returns
    False if no buffering is necessary (configuration) or possible (locked)
    True if buffering has been handled
    
    """
    
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
