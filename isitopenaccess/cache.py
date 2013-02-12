import redis, json, datetime, logging
import config

log = logging.getLogger(__name__)

def check_cache(key):
    """
    check the cache for an object stored under the given key, and convert it
    from a string into a python object
    """
    client = redis.StrictRedis(host=config.redis_cache_host, port=config.redis_cache_port, db=config.redis_cache_db)
    s = client.get(key)
    
    if s is None:
        return None
    
    try:
        obj = json.loads(s)
    except ValueError as e:
        # cache is corrupt, just get rid of it
        invalidate(key)
        return None
    
    return obj
    
def is_stale(bibjson):
    """
    Check to see if the bibjson record in the supplied record is stale.  Look
    in bibjson['license'][n]['provenance']['date'] for all n.  If the newest date
    is older than the stale time, then the record is stale.  If the record does
    not have a licence, it is stale.
    """
    # check that the record has a licence at all
    if not bibjson.has_key("license"):
        return True
    
    # get the date strings of all the licences
    date_strings = [licence.get("provenance", {}).get("date") 
                for licence in bibjson.get("license", []) 
                if licence.get("provenance", {}).get("date") is not None]
    
    # check that there were any dates, if not then the record is necessarily stale
    if len(date_strings) == 0:
        return True
    
    # convert all the viable date strings to datetimes
    dates = []
    for d in date_strings:
        try:
            dt = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
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
    """
    client = redis.StrictRedis(host=config.redis_cache_host, port=config.redis_cache_port, db=config.redis_cache_db)
    client.delete(key)
    
def cache(key, obj):
    """
    take the provided python data structure, serialise it via json to a string, and
    store it at the provided key with the appropriate timeout.  This may be
    required to create a new cache entry or update an existing one
    """
    try:
        s = json.dumps(obj)
    except TypeError:
        raise CacheException("can only cache python objects that can be sent through json.dumps")
    
    client = redis.StrictRedis(host=config.redis_cache_host, port=config.redis_cache_port, db=config.redis_cache_db)
    client.setex(key, config.redis_cache_timeout, s)
    
class CacheException(Exception):
    def __init__(self, message):
        self.message = message
        super(CacheException, self).__init__(self, message)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
