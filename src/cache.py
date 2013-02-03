def check_cache(key):
    """
    check the cache for an object stored under the given key, and convert it
    from a string into a python object
    """
    pass
    
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
    pass
    
def cache(key, obj):
    """
    take the provided python data structure, serialise it to a string, and
    store it at the provided key with the appropriate timeout.  This may be
    required to create a new cache entry or update an existing one
    """
    pass
