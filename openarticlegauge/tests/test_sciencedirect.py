from unittest import TestCase
import os

from openarticlegauge import config, models, util

######################################################################################
# Set these variables/imports and the test case will use them to perform some general
# tests on your provider code

from openarticlegauge.plugins.sciencedirect import ScienceDirectPlugin as MyPlugin

# a list of urls which your plugin should be able to support
SUPPORTED_URLS = ["http://www.sciencedirect.com/science/article/pii/S003040261300257X",
                  "http://www.sciencedirect.com/science/article/pii/S002199911400031X",
    "http://sciencedirect.com/this_is_just_a_string_format_test_lets_try_without_www"]

# a list of urls which your plugin SHOULD NOT be able to support
UNSUPPORTED_URLS = ["http://www.biomedcentral.com/", "askjdfsakjdhfsa"]

# a list of file paths and the expected licence object from parsing that file path
#
# in the examples here we construct file paths that are relative to this test class
# in the "resources" sub-directory.  If you put your test documents in there, then
# all you need to change is the filename, which is the final argument passed os.path.join
#
# The licence object is as defined in the OAG API documentation.  Any fields omitted will
# not be checked.  Any fields included will be checked for an exact match against the actual
# record received when the plugin is run.  See below for the full spec of the licence
# object.
#
# The rules for the comparison licence object are:
# - if a key has a value, there resulting object's value must match exactly
# - if a key has been omitted, it will not be tested
# - if a key's value is the empty string, the resulting object's key's value must be the empty string
# - if a key's value is None, the resulting object MUST NOT have the key or MUST be the empty string
# - if a key's value is -1, the resulting object MUST have the key
#

RESOURCE_AND_RESULT = {
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.jcp.2014.01.010.xml") :
        {
            "id" : None,            # there should be no id field
            "version": "3.0",       # version should be 3.0
            "type": "cc-by-nc-nd",        # type is cc-by
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": False,
            "BY": True,
            "NC": True,
            "ND": True,
            "SA": False,
            "provenance": {
                "handler": 'sciencedirect', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "xml_api", # category is xml_api
                "description": 'License decided by querying the Elsevier XML API at http://api.elsevier.com/content/article/doi:10.1016/j.jcp.2014.01.010', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://api.elsevier.com/content/article/doi:10.1016/j.jcp.2014.01.010", # source is the url where we look this record up
                "source_size" : 1663, # the expected number of bytes
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.aasri.2013.10.051.xml") :
        {
            "id" : None,            # there should be no id field
            "version": "",          # version should be blank
            "type": "free-to-read",
            "jurisdiction": "",     # jurisdiction should be the empty string
            # rights fields - just check that they are present
            "open_access": -1,
            "BY": -1,
            "NC": -1,
            "ND": -1,
            "SA": -1,
            "provenance": {
                "handler": 'sciencedirect', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "xml_api", # category is xml_api
                "description": 'License decided by querying the Elsevier XML API at http://api.elsevier.com/content/article/doi:10.1016/j.aasri.2013.10.051', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://api.elsevier.com/content/article/doi:10.1016/j.aasri.2013.10.051", # source is the url where we look this record up
                "source_size" : 1557, # the expected number of bytes
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.cortex.2013.08.002.xml") :
        {
            "id" : None,            # there should be no id field
            "version": "3.0",          # version should be blank
            "type": "cc-by",
            "jurisdiction": "",     # jurisdiction should be the empty string
            # rights fields - just check that they are present
            "open_access": True,
            "BY": True,
            "NC": False,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'sciencedirect', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "xml_api", # category is xml_api
                "description": 'License decided by querying the Elsevier XML API at http://api.elsevier.com/content/article/doi:10.1016/j.cortex.2013.08.002', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://api.elsevier.com/content/article/doi:10.1016/j.cortex.2013.08.002", # source is the url where we look this record up
                "source_size" : 1636, # the expected number of bytes
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
}

# which file corresponds to which DOI, needed to provide > 1 mock provider record to the plugin
DOIS = {
    # Elsevier's API requires the doi: prefix, so keep it there
    # any identifiers coming in from the outside will be resolved by the DOI plugin, which always canonicalises DOI-s to have that prefix
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.jcp.2014.01.010.xml"): 'doi:10.1016/j.jcp.2014.01.010',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.aasri.2013.10.051.xml"): 'doi:10.1016/j.aasri.2013.10.051',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "sciencedirect_j.cortex.2013.08.002.xml"): 'doi:10.1016/j.cortex.2013.08.002'
}



"""
Full specification of the OAG licence object, as taken from the API documentation:
{
    "status": "active",
    "maintainer": "",
    "description": "",
    "family": ""
    "title": "Creative Commons Attribution",
    "domain_data": true/false,
    "url": "http://www.opendefinition.org/licenses/cc-by",                
    "version": "",
    "domain_content": true/false,
    "is_okd_compliant": true/false,
    "is_osi_compliant": true/false,
    "domain_software": true/false,
    "type": "cc-by",
    "jurisdiction": "",
    "open_access": true/false,
    "BY": true/false,
    "NC": true/false,
    "ND": true/false,
    "SA": true/false,
    "provenance": {
        "category": "page_scrape",
        "description": "how the content was acquired ...",
        "agent": "OpenArticleGauge Service/0.1 alpha",
        "source": "http://www.plosbiology.org/article/info%3Adoi%2F10...",
        "source_size" : source_size_in_bytes,
        "date": "2013-02-16T21:51:54.669040"
    }
}
"""
################################################################################

CURRENT_REQUEST = None

# Mock response object for the requests library.  If your provider does anything other
# than look at the http response and the page content you will need to extend this
class MockResponse():
    def __init__(self):
        self.status_code = None
        self.text = None
        self.content = None
        self.url = None
    
def mock_get(url, *args, **kwargs):
    resp = MockResponse()
    resp.status_code = 200
    resp.url = CURRENT_REQUEST
    resp.headers = {'content-length': 100}
    for filename, obj in RESOURCE_AND_RESULT.iteritems():
        if obj['provenance']['source'] == CURRENT_REQUEST:
            with open(filename) as f:
                resp.text = f.read()
            break
    resp.content = resp.text

    def return_all_content(*args, **kwargs):
        return resp.content

    resp.iter_content = return_all_content

    class MockConnection(object):
        @staticmethod
        def close():
            return True
    resp.connection = MockConnection()

    return resp

class TestProvider(TestCase):

    def setUp(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        self.old_get = util.http_get
        util.http_get = mock_get
        
    def tearDown(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        util.http_get = self.old_get

    def test_01_supports_success(self):
        p = MyPlugin()
        for url in SUPPORTED_URLS:
            assert p.supports({"url" : [url]})
        
    def test_02_supports_fail(self):
        p = MyPlugin()
        for url in UNSUPPORTED_URLS:
            assert not p.supports({"url" : [url]})
    
    def test_03_resource_and_result(self):
        global CURRENT_REQUEST
        
        # go through each file and result object
        for path, comparison in RESOURCE_AND_RESULT.iteritems():
            # construct a request object, using the provenance/source url as the provider url
            record = {}
            record['bibjson'] = {}
            record['provider'] = {}
            record['provider']['url'] = [comparison['provenance']['source']]
            record['provider']['doi'] = DOIS[path]
            record = models.MessageObject(record=record)
            
            # set the current request so that the monkey patch knows how to respond
            CURRENT_REQUEST = comparison['provenance']['source']
            
            # run the plugin
            p = MyPlugin()
            p.license_detect(record)
            
            record = record.record
            
            # check if all the top-level keys were created
            assert "bibjson" in record
            assert "license" in record['bibjson'], 'No license when testing file ' + path
            assert record['bibjson']['license'] is not None
            
            # The rules for the comparison licence object are:
            # - if a key has a value, there resulting object's value must match exactly
            # - if a key has been omitted, it will not be tested
            # - if a key's value is the empty string, the resulting object's key's value must be the empty string
            # - if a key's value is None, the resulting object MUST NOT have the key or MUST be the empty string
            # - if a key's value is -1, the resulting object MUST have the key
            licence = record['bibjson']['license'][0]
            for key, value in comparison.iteritems():
                if key == "provenance":
                    # for better layout of code, let's do provenance separately
                    continue
                if value is None:
                    # the resulting object MUST NOT have the key or MUST be the empty string
                    assert key not in licence or licence.get(key) == "", ((key, value), licence.get(key))
                elif value == -1:
                    # the resulting object MUST have the key
                    assert key in licence, ((key, value), licence.get(key))
                else:
                    # the resulting object must match the comparison object
                    assert value == licence.get(key), ((key, value), licence.get(key))
            
            prov = licence.get("provenance", {})
            for key, value in comparison.get("provenance", {}).iteritems():
                if value is None:
                    # the resulting object MUST NOT have the key
                    assert key not in prov or prov.get(key) == "", ((key, value), prov.get(key))
                elif value == -1:
                    # the resulting object MUST have the key
                    assert key in prov, ((key, value), prov.get(key))
                else:
                    # the resulting object must match the comparison object
                    assert value == prov.get(key), ((key, value), prov.get(key))
