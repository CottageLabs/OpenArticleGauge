# how to run the iioa app
host = '0.0.0.0'
port = '5000'
debug = True

# provide an email address for receiving errors or dispute warning
contact_email = ''

# packages that the plugloader should look in to find callable plugins if
# it can't find them straight away in the running context.  Note that an installed
# application and an application run from its directory will have different
# running contexts, so this is important.
module_search_list = ["isitopenaccess"]

# List of plugins that will run in order to detect the type of an identifier.
# All plugins will run
type_detection = [
    "isitopenaccess.plugins.doi.DOIPlugin",
    "isitopenaccess.plugins.pmid.PMIDPlugin"
]

# dictionary of plugins that can be used to canonicalise all the different 
# identifier types.  Key is the identifier type as detected with type_detection,
# value is the plugin to be used
canonicalisers = {
    "doi" : "isitopenaccess.plugins.doi.DOIPlugin",
    "pmid" : "isitopenaccess.plugins.pmid.PMIDPlugin"
}

# dictionary of lists of plugins that can be used to determine the provider
# of an identifier type.  Key is the identifier type as detected with type_detection,
# value is a list of plugins to be run in order.  When a plugin detects a provider,
# processing of the chain will exit without passing any further.
provider_detection = {
    "doi" : ["isitopenaccess.plugins.doi.DOIPlugin"], 
    "pmid" : ["isitopenaccess.plugins.pmid.PMIDPlugin"]
}

# dictionary of single plugins that can be used to determine the licence 
# conditions of a given identifier.  Key is a string representing the provider,
# value is a singple plugin to be run.  Plugins are selected based on selecting
# the MOST GRANULAR or MOST SPECIFIC plugin
#
# NOTE: URLs should be presented without leading http or https protocol specifiers
# (so https://www.plosone.org should be www.plosone.org)
license_detection = [
    "isitopenaccess.plugins.plos.PLOSPlugin",
    "isitopenaccess.plugins.bmc.BMCPlugin",
    "isitopenaccess.plugins.cell_reports.CellReportsPlugin",
    "isitopenaccess.plugins.oup.OUPPlugin",
    "isitopenaccess.plugins.elife.ELifePlugin"
]

# Cache configuration
redis_cache_host = "localhost"
redis_cache_port = 6379
redis_cache_db = 2
redis_cache_timeout = 7776000 # approximately 3 months

# Number of seconds it takes for a licence record to be considered stale
licence_stale_time = 15552000 # approximately 6 months

# whether or not we are buffering posts to the index
buffering = False

# elasticsearch configs
es_address = 'http://localhost:9200'
es_indexname = 'iioa'
es_indextype = 'record'
es_disputetype = 'dispute'

# if index does not exist, it will be created first time round using the mapping below
es_mapping = {
    "record" : {
        "date_detection" : "false",
        "dynamic_templates" : [
            {
                "default" : {
                    "match" : "*",
                    "match_mapping_type": "string",
                    "mapping" : {
                        "type" : "multi_field",
                        "fields" : {
                            "{name}" : {"type" : "{dynamic_type}", "index" : "analyzed", "store" : "no"},
                            "exact" : {"type" : "{dynamic_type}", "index" : "not_analyzed", "store" : "yes"}
                        }
                    }
                }
            }
        ]
    }
}


# IIOA version and user agent string
version = '0.1 alpha'
agent = 'IsItOpenAccess Service/' + version

# Date format to be used throughout the system
date_format = "%Y-%m-%dT%H:%M:%SZ"

# urls to be used by plugins or the processing pipeline when the licence cannot be detected
unknown_url = ""
known_unknown_url = ""

