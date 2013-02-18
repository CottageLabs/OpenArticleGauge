# how to run the iioa app
host = '0.0.0.0'
port = '5000'
debug = True

# packages that the plugloader should look in to find callable plugins if
# it can't find them straight away in the running context.  Note that an installed
# application and an application run from its directory will have different
# running contexts, so this is important.
module_search_list = ["isitopenaccess"]

# List of plugins that will run in order to detect the type of an identifier.
# All plugins will run
type_detection = [
    "plugins.doi.type_detect_verify",
    "plugins.pmid.type_detect_verify"
]

# dictionary of plugins that can be used to canonicalise all the different 
# identifier types.  Key is the identifier type as detected with type_detection,
# value is the plugin to be used
canonicalisers = {
    "doi" : "plugins.doi.canonicalise",
    "pmid" : "plugins.pmid.canonicalise"
}

# dictionary of lists of plugins that can be used to determine the provider
# of an identifier type.  Key is the identifier type as detected with type_detection,
# value is a list of plugins to be run in order.  When a plugin detects a provider,
# processing of the chain will exit without passing any further.
provider_detection = {
    "doi" : ["plugins.doi.provider_range_lookup", "plugins.doi.provider_dereference"], 
    "pmid" : ["plugins.pmid.provider_resolver"]
}

# dictionary of single plugins that can be used to determine the licence 
# conditions of a given identifier.  Key is a string representing the provider,
# value is a singple plugin to be run.  Plugins are selected based on selecting
# the MOST GRANULAR or MOST SPECIFIC plugin
licence_detection = {
    # PLoS
    "www.plosone.org" : "plugins.plos.page_license",
    "www.plosbiology.org" : "plugins.plos.page_license",
    "www.plosmedicine.org" : "plugins.plos.page_license",
    "www.ploscompbiol.org" : "plugins.plos.page_license",
    "www.plosgenetics.org" : "plugins.plos.page_license",
    "www.plospathogens.org" : "plugins.plos.page_license",
    "www.plosntds.org" : "plugins.plos.page_license",
    # BMC
    "www.biomedcentral.com" : "plugins.bmc.page_license"
}

# Cache configuration
redis_cache_host = "localhost"
redis_cache_port = 6379
redis_cache_db = 2
redis_cache_timeout = 7776000 # approximately 3 months

# Number of seconds it takes for a licence record to be considered stale
licence_stale_time = 15552000 # approximately 6 months

# bibserver configs
bibserver_address = 'http://bibsoup.net'
bibserver_api_key = '' # valid api_key for a user on the addressed bibserver - REQUIRED if bibserver is not on localhost
bibserver_collection = 'isitopenaccess' # collection name that we will put IIOA files into
bibserver_buffering = False # whether or not we are buffering posts to bibserver

# elasticsearch configs - if running bibserver locally or you want to talk direct to ES instead, these will be used
es_address = 'http://localhost:9200' # if this is set, it is used in preference to the bibserver_address above. So leave blank otherwise
es_indexname = 'iioa' # NO ATTEMPT IS MADE TO CREATE THESE - IIOA assumes your index is ready to go (which it will be if you use bibserver)
es_indextype = 'record'

# IIOA version and user agent string
version = '0.1 alpha'
agent = 'IsItOpenAccess Service/' + version
