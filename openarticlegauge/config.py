# how to run the oag app
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
module_search_list = ["openarticlegauge"]

# List of plugins that will run in order to detect the type of an identifier.
# All plugins will run
type_detection = [
    "openarticlegauge.plugins.doi.DOIPlugin",
    "openarticlegauge.plugins.pmid.PMIDPlugin"
]

# dictionary of plugins that can be used to canonicalise all the different 
# identifier types.  Key is the identifier type as detected with type_detection,
# value is the plugin to be used
canonicalisers = {
    "doi" : "openarticlegauge.plugins.doi.DOIPlugin",
    "pmid" : "openarticlegauge.plugins.pmid.PMIDPlugin"
}

# dictionary of lists of plugins that can be used to determine the provider
# of an identifier type.  Key is the identifier type as detected with type_detection,
# value is a list of plugins to be run in order.  When a plugin detects a provider,
# processing of the chain will exit without passing any further.
provider_detection = {
    "doi" : ["openarticlegauge.plugins.doi.DOIPlugin"], 
    "pmid" : ["openarticlegauge.plugins.pmid.PMIDPlugin"]
}

# plugins which may support publisher pages
license_detection = [
    "openarticlegauge.plugins.plos.PLOSPlugin",
    "openarticlegauge.plugins.bmc.BMCPlugin",
    "openarticlegauge.plugins.cell_reports.CellReportsPlugin",
    "openarticlegauge.plugins.oup.OUPPlugin",
    "openarticlegauge.plugins.elife.ELifePlugin",
    "openarticlegauge.plugins.nature.NaturePlugin",
    "openarticlegauge.plugins.copernicus.COPERNICUSPlugin",
]

# Cache configuration
REDIS_CACHE_HOST = "localhost"
REDIS_CACHE_PORT = 6379
REDIS_CACHE_DB = 2
REDIS_CACHE_TIMEOUT = 7776000 # approximately 3 months

# Number of seconds it takes for a licence record to be considered stale
licence_stale_time = 15552000 # approximately 6 months

# whether or not we are buffering posts to the index
BUFFERING = True

# period of time in which to aim to flush the buffer to the archive.
# The actual time period may vary for a number of reasons, including overrun
# of a previous buffering job.  For example, if the buffer flush period is set to 10
# seconds and the time taken to do the buffering is 15 seconds, then the 
# buffer flush period will practically work out to be every 20 seconds
BUFFER_FLUSH_PERIOD = 30

# period of time after sending the buffer to Elastic Search to wait before
# removing buffered items from the buffer.  This allows ES to process and refresh
# itself and be ready to be queried before the buffered versions of the
# records get removed.  This number should be a lot less than the BUFFER_FLUSH_PERIOD
# as otherwise they'll keep tripping over eachother
BUFFER_GRACE_PERIOD = 10

# Redis buffer configuration
REDIS_BUFFER_HOST = "localhost"
REDIS_BUFFER_PORT = 6379
REDIS_BUFFER_DB = 3

# elastic search buffer bulk loading block size - the maximum number of items
# permitted in a single elastic search bulk request
BUFFER_BLOCK_SIZE = 1000

# elasticsearch configs
ELASTIC_SEARCH_HOST = 'http://localhost:9200'
ELASTIC_SEARCH_DB = 'oag'
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

# OAG version and user agent string
version = '0.1 alpha'
agent = 'OpenArticleGauge Service/' + version

# Date format to be used throughout the system
date_format = "%Y-%m-%dT%H:%M:%SZ"

# urls to be used by plugins or the processing pipeline when the licence cannot be detected
unknown_url = ""
known_unknown_url = ""

