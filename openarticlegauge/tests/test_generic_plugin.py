from unittest import TestCase
import os

from openarticlegauge import config, models, util

######################################################################################
# Set these variables/imports and the test case will use them to perform some general
# tests on your provider code

# import your plugin as "MyPlugin" (here, replace "plos" and "PLOSPlugin" with your plugin module's name and class)
from openarticlegauge.plugins._ubiquitous import UbiquitousPlugin as MyPlugin

# a list of urls which your plugin should be able to support
SUPPORTED_URLS = ["http://www.plosone.org/1234",
    "http://www.anything-which.looks/like_a_url?should+be+supported",
    "http://or rather, whatever the requests library thinks is valid"]

# a list of urls which your plugin SHOULD NOT be able to support
UNSUPPORTED_URLS = ['''anything that's not a valid URL is not supported
    even by the generic plugin''', "askjdfsakjdhfsa",

    "www.plosbiology.org/fakjsskjdaf" # note it does not have a schema -
        # it's an invalid URL. The other plugins support such URL-s
        # since they actually prefer schema-less URL-s for string
        # comparisons (when they want to check whether they support a
        # particular provider as identified by the URL). The generic
        # plugin can't do this - it doesn't use string comparison to
        # check whether it supports a provider or not. Plus we cannot
        # add arbitrary schemas to schema-less URL-s!
]

# a list of file paths and the expected licence object from parsing that file path
#
# in the examples here we construct file paths that are relative to this test class
# in the "resources" sub-directory.  If you put your test documents in there, then
# all you need to change is the filename, which is the final argument passed os.path.join
#
# the example file used resources/pbio1001406.html is a plos web page
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
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "pbio.1001406.html") : 
        {
            "id" : None,            # there should be no id field
            "version": "",          # version should be the empty string
            "type": "cc-by",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": True,
            "BY": True,
            "NC": False,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'ubiquitous', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": 'License decided by scraping the resource at http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406 and looking for the following license statement: "under the terms of the Creative Commons Attribution License".', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
       },

    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "ubiquity_ai-journal_247.html") : 
        {
            "id" : None,            # there should be no id field
            "version": "3.0",
            "type": "cc-by",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": True,
            "BY": True,
            "NC": False,
            "SA": False,
            "ND": False,
            "provenance": {
                "handler": MyPlugin._short_name, # name of plugin which processed this record
                "handler_version": MyPlugin.__version__, # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": '''License decided by scraping the resource at http://www.ai-journal.com/article/view/247 and looking for the following license statement: "under the terms of the Creative Commons Attribution License <br/>(<a href="http://creativecommons.org/licenses/by/3.0" target="_blank">http://creativecommons.org/licenses/by/3.0</a>)".''', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://www.ai-journal.com/article/view/247", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
       },
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

    return resp, resp.content, len(resp.content)

class TestProvider(TestCase):

    def setUp(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        self.old_get = util.http_stream_get
        util.http_stream_get = mock_get
        
    def tearDown(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        util.http_stream_get = self.old_get

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
            record = models.MessageObject(record=record)
            
            # set the current request so that the monkey patch knows how to respond
            CURRENT_REQUEST = comparison['provenance']['source']
            
            # run the plugin
            p = MyPlugin()
            p.license_detect(record)

            record = record.record
            
            # check if all the top-level keys were created
            assert "bibjson" in record
            assert "license" in record['bibjson']
            assert record['bibjson']['license'] is not None
            assert len(record['bibjson']['license']) == 1 # only 1
                # license was detected
            
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
