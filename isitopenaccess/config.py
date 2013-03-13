# how to run the iioa app
SECRET_KEY = 'reallysecret...'
HOST = '0.0.0.0'
PORT = '5000'
DEBUG = True
MAX_CONTENT_LENGTH = 1024 * 1024 * 3
NO_QUERY_VIA_API = []
ANONYMOUS_SEARCH_FILTER = False
SEARCH_SORT = False

# provide an email address for receiving errors or dispute warning
CONTACT_EMAIL = ''

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
REDIS_CACHE_HOST = "localhost"
REDIS_CACHE_PORT = 6379
REDIS_CACHE_DB = 2
REDIS_CACHE_TIMEOUT = 7776000 # approximately 3 months

# Number of seconds it takes for a licence record to be considered stale
licence_stale_time = 15552000 # approximately 6 months

# whether or not we are buffering posts to the index
BUFFERING = False

# elasticsearch configs
ELASTIC_SEARCH_HOST = 'http://localhost:9200'
ELASTIC_SEARCH_DB = 'iioa'
INITIALISE_INDEX = True

# if index does not exist, it will be created first time round using the mapping below
FACET_FIELD = '.exact'
MAPPINGS = {
    "record": {
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
}
MAPPINGS['dispute'] = {'dispute':MAPPINGS['record']['record']}
MAPPINGS['log'] = {'log':MAPPINGS['record']['record']}

# IIOA version and user agent string
version = '0.1 alpha'
agent = 'IsItOpenAccess Service/' + version

# Date format to be used throughout the system
date_format = "%Y-%m-%dT%H:%M:%SZ"

# urls to be used by plugins or the processing pipeline when the licence cannot be detected
unknown_url = ""
known_unknown_url = ""

