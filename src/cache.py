import redis, json
import config



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
    in record['bibjson']['license'][n]['provenance']['date'] for all n
    """
    return False
    
def invalidate(key):
    """
    remove anything identified by the supplied key from the cache
    """
    client = redis.StrictRedis(host=config.redis_cache_host, port=config.redis_cache_port, db=config.redis_cache_db)
    client.delete(key)
    
def cache(key, obj):
    """
    take the provided python data structure, serialise it to a string, and
    store it at the provided key with the appropriate timeout.  This may be
    required to create a new cache entry or update an existing one
    """
    pass
