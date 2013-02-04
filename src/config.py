import plugins

# List of plugins that will run in order to detect the type of an identifier.
# All plugins will run
type_detection = [
    plugins.doi.type_detect_verify,
    plugins.pmid.type_detect_verify
]

# dictionary of plugins that can be used to canonicalise all the different 
# identifier types.  Key is the identifier type as detected with type_detection,
# value is the plugin to be used
canonicalisers = {
    "doi" : plugins.doi.canonicalise,
    "pmid" : plugins.pmid.canonicalise
}

# dictionary of lists of plugins that can be used to determine the provider
# of an identifier type.  Key is the identifier type as detected with type_detection,
# value is a list of plugins to be run in order.  When a plugin detects a provider,
# processing of the chain will exit without passing any further.
provider_detection = {
    "doi" : [plugins.doi.provider_range_lookup, plugins.doi.provider_dereference], 
    "pmid" : [plugins.pmid.provider_resolver]
}

# dictionary of single plugins that can be used to determine the licence 
# conditions of a given identifier.  Key is a string representing the provider,
# value is a singple plugin to be run.  Plugins are selected based on selecting
# the MOST GRANULAR or MOST SPECIFIC plugin
licence_detection = {
    "http://www.plos.com/" : plugins.plos.site_wide_licence
}

# Cache configuration
redis_cache_host = "localhost"
redis_cache_port = 6379
redis_cache_db = 2
