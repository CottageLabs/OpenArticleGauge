"""
Implementation of all functions which allow the OAG application to interface with
the cache.

This cache implementation uses Redis as a key/value store in which to place json
serialised copies of python data structures passed in.  Keys used are up to the
implementing code, but should be the canonical representations of the record being cached
identifier.

"""

import redis, json, datetime, logging, models
import config

log = logging.getLogger(__name__)

def check_cache(key):
    """
    check the cache for an object stored under the given key, and convert it
    from a string into a python object
    
    arguments:
    key -- the key to look up in the cache.  This should be the canonical identifier of the item being looked up
    
    returns
    - None if the object couldn't be found in the cache, or there is an error with the cached object
    - A python data structure if one can be found, which will hopefully be a bibjson record if you stored it right
    
    """
    client = redis.StrictRedis(host=config.REDIS_CACHE_HOST, port=config.REDIS_CACHE_PORT, db=config.REDIS_CACHE_DB)
    s = client.get(key)
    
    if s is None:
        return None
    
    try:
        obj = json.loads(s)
    except ValueError as e:
        # cache is corrupt, just get rid of it
        invalidate(key)
        return None
    
    # return obj
    return models.MessageObject(record=obj)
    
# def is_stale(bibjson):
def is_stale(record):
    """
    Check to see if the bibjson record in the supplied record is stale.  Look
    in bibjson['license'][n]['provenance']['date'] for all n.  If the newest date
    is older than the stale time, then the record is stale.  If the record does
    not have a licence, it is stale.
    
    arguments:
    bibjson -- a bibjson record in a python datastructure.  It may contain zero or more
        licence statements which meet the OAG specification for licence records (see the
        top level documentation for details)
    
    returns:
    - True if there is no licence in the object or the most recently applied licence is older than the configured stale timeout (see config)
    - False if there is a licence in the object and it is newer than the configured stale timeout (see config)
    
    """
    # check that the record has a licence at all
    if not record.has_license():
        return True
    
    # get the date strings of all the licences
    log.debug("stale check on: " + str(record.bibjson))
    date_strings = [licence.get("provenance", {}).get("date") 
                for licence in record.bibjson.get("license", []) 
                if licence.get("provenance", {}).get("date") is not None]
    
    # check that there were any dates, if not then the record is necessarily stale
    if len(date_strings) == 0:
        return True
    
    # convert all the viable date strings to datetimes
    dates = []
    for d in date_strings:
        try:
            dt = datetime.datetime.strptime(d, config.date_format)
            dates.append(dt)
        except ValueError as e:
            continue
    
    # check that at least one date has parsed, and if not assume that the record is stale
    if len(dates) == 0:
        return True
    
    # get the most recent date by sorting the list (reverse, most recent date first)
    dates.sort(reverse=True)
    most_recent = dates[0]
    
    # now determine if the most recent date is older or newer than the stale timeout
    td = datetime.timedelta(seconds=config.licence_stale_time)
    n = datetime.datetime.now()
    stale_date = most_recent + td
    return stale_date < n
    
def invalidate(key):
    """
    remove anything identified by the supplied key from the cache
    
    arguments:
    key -- the key to be removed from the cache.  This should be the canonical identifier of the record concerned
    
    """
    client = redis.StrictRedis(host=config.REDIS_CACHE_HOST, port=config.REDIS_CACHE_PORT, db=config.REDIS_CACHE_DB)
    client.delete(key)
    
def cache(key, record):
    """
    take the provided python data structure, serialise it via json to a string, and
    store it at the provided key with the appropriate timeout.  This may be
    required to create a new cache entry or update an existing one
    
    arguments:
    key -- the key under which to store the item in the cache.  This shold be the canonical identifier of the record concerned
    obj -- a python data structure which is serialisable to json
    
    """
    try:
        s = record.json()
        # s = json.dumps(obj)
    except TypeError:
        raise CacheException("can only cache python objects that can be sent through json.dumps")
    except AttributeError:
        raise CacheException("record object does not support json() attribute - you should use a MessageObject")
    
    client = redis.StrictRedis(host=config.REDIS_CACHE_HOST, port=config.REDIS_CACHE_PORT, db=config.REDIS_CACHE_DB)
    client.setex(key, config.REDIS_CACHE_TIMEOUT, s)
    
class CacheException(Exception):
    """
    Exception class to handle any problems arising in the cache
    
    """
    def __init__(self, message):
        self.message = message
        super(CacheException, self).__init__(self, message)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
