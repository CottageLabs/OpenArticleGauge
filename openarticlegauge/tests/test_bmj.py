from time import sleep
from unittest import TestCase
import requests, os

from openarticlegauge import config, models

######################################################################################
# Set these variables/imports and the test case will use them to perform some general
# tests on your provider code

# import your plugin as "MyPlugin" (here, replace "plos" and "PLOSPlugin" with your plugin module's name and class)
from openarticlegauge.plugins.bmj import BMJPlugin as MyPlugin

# a list of urls which your plugin should be able to support
SUPPORTED_URLS = ["http://www.bmj.com/content/345/bmj.e8050", 
				  "http://gut.bmj.com/content/early/2013/08/20/gutjnl-2013-305008", 
				  "http://thorax.bmj.com/content/68/1/82",
				  "http://bjo.bmj.com/content/98/3/377"]

# a list of urls which your plugin SHOULD NOT be able to support
UNSUPPORTED_URLS = ["springer.com/article", "sciencedirect.com/article", "http://www.plosone.org/", "askjdfsakjdhfsa"]

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
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "bmj_10.1136_bmj.e8050.html"):
        {
            "id" : None,            # there should be no id field
            "version": "2.0",          # version should be the empty string
            "type": "cc-nc",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": False,
            "BY": True,
            "NC": True,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'bmj', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": 'License decided by scraping the resource at http://www.bmj.com/content/345/bmj.e8050 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits use, distribution, and reproduction in any medium, provided the original work is properly cited, the use is non commercial and is otherwise in compliance with the license. See: <a href="http://creativecommons.org/licenses/by-nc/2.0/">http://creativecommons.org/licenses/by-nc/2.0/</a>".', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://www.bmj.com/content/345/bmj.e8050", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "bmj_10.1136_gutjnl-2013-305008.html"):
        {
            "id" : None,            # there should be no id field
            "version": "3.0",          # version should be the empty string
            "type": "cc-by",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": True,
            "BY": True,
            "NC": False,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'bmj', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": 'License decided by scraping the resource at http://gut.bmj.com/content/early/2013/08/20/gutjnl-2013-305008 and looking for the following license statement: "This is an Open Access article distributed in accordance with the terms of the Creative Commons Attribution (CC BY 3.0) license, which permits others to distribute, remix, adapt and build upon this work, for commercial use, provided the original work is properly cited. See: <a href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>".', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://gut.bmj.com/content/early/2013/08/20/gutjnl-2013-305008", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "bmj_10.1136_bjophthalmol-2013-304179.html"):
        {
            "id" : None,            # there should be no id field
            "version": "3.0",          # version should be the empty string
            "type": "cc-nc",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": False,
            "BY": True,
            "NC": True,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'bmj', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": 'License decided by scraping the resource at http://bjo.bmj.com/content/98/3/377 and looking for the following license statement: "This is an Open Access article distributed in accordance with the Creative Commons Attribution Non Commercial (CC BY-NC 3.0) license, which permits others to distribute, remix, adapt, build upon this work non-commercially, and license their derivative works on different terms, provided the original work is properly cited and the use is non-commercial. See: <a href="http://creativecommons.org/licenses/by-nc/3.0/">http://creativecommons.org/licenses/by-nc/3.0/</a>".', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://bjo.bmj.com/content/98/3/377", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
        },
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "bmj_10.1136_thoraxjnl-2012-202003.html"):
        {
            "id" : None,            # there should be no id field
            "version": "3.0",          # version should be the empty string
            "type": "cc-nc",
            "jurisdiction": "",     # jurisdiction should be the empty string
            "open_access": False,
            "BY": True,
            "NC": True,
            "ND": False,
            "SA": False,
            "provenance": {
                "handler": 'bmj', # name of plugin which processed this record
                "handler_version": '0.1', # version of plugin which processed this record
                "category": "page_scrape", # category is page_scrape
                "description": 'License decided by scraping the resource at http://thorax.bmj.com/content/68/1/82 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits use, distribution, and reproduction in any medium, provided the original work is properly cited, the use is non commercial and is otherwise in compliance with the license. See: <a href="http://creativecommons.org/licenses/by-nc/3.0/">http://creativecommons.org/licenses/by-nc/3.0/</a>".', # description is a long string
                "agent": config.agent, # agent is from configuration
                "source": "http://thorax.bmj.com/content/68/1/82", # source is the url where we look this record up
                "date": -1 # date is not null (but we don't know the exact value)
            }
        }

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
        self.old_get = requests.get
        requests.get = mock_get
        
    def tearDown(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        requests.get = self.old_get

    def test_01_supports_success(self):
        p = MyPlugin()
        for url in SUPPORTED_URLS:
            assert p.supports({"url" : [url]})
        
    def test_02_supports_fail(self):
        p = MyPlugin()
        for url in UNSUPPORTED_URLS:
            assert not p.supports({"url" : [url]}), "Failed with URL " + url

    def __run_resource_and_result_test(self):
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
            assert "license" in record['bibjson'], 'While testing with ' + path
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

    def test_03_resource_and_result_with_hardcoded_lic_statements(self):
        self.__run_resource_and_result_test()

#     def test_04_resource_and_result_with_publisher_config(self):
#         springer_config = models.Publisher()
#         springer_config.publisher_name = 'SpringerLink'
#         springer_config.journal_urls = ['link.springer.com']
#         springer_config.licenses = [
#             {
#                 'license_statement': 'This article is distributed under the terms of the Creative Commons Attribution License which permits any use, distribution, and reproduction in any medium, provided the original author(s) and the source are credited.',
#                 'license_type': 'cc-by',
#                 'version': '',
#                 'example_doi': '10.1007/s10522-013-9457-0'
#             }
#         ]
#         springer_config.save()
#         sleep(2)  # let the index catch up
#         self.__run_resource_and_result_test()
#         springer_config.delete()