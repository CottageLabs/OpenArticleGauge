from unittest import TestCase
import requests, os
import time

from openarticlegauge import config, models

######################################################################################
# Set these variables/imports and the test case will use them to perform some general
# tests on your provider code

# import your plugin as "MyPlugin" (here, replace "plos" and "PLOSPlugin" with your plugin module's name and class)
from openarticlegauge.plugins.generic_string_matcher import GenericStringMatcherPlugin as MyPlugin

# a list of urls which your plugin should be able to support
#SUPPORTED_URLS = ["http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0031314"]
SUPPORTED_URLS = ["www.plosone.org"]

# a list of urls which your plugin SHOULD NOT be able to support
UNSUPPORTED_URLS = [ ]

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
    # the following cases should be matched by GSM configs
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "pone.0031314.html"):
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
            "handler": 'PLOS', # name of plugin which processed this record
            "handler_version": '0.2', # version of plugin which processed this record
            "category": "page_scrape", # category is page_scrape
            "description": 'License decided by scraping the resource at http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0031314 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.".', # description is a long string
            "agent": config.agent, # agent is from configuration
            "source": "http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0031314", # source is the url where we look this record up
            "date": -1 # date is not null (but we don't know the exact value)
        }
    },
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "10.1111_j.1365-2869.2012.01054.x.html"):
    {
        "id" : None,            # there should be no id field
        "version": "",          # version should be the empty string
        "type": "free-to-read",
        "jurisdiction": "",     # jurisdiction should be the empty string
        # rights fields - just check that they are present
        "open_access": -1,
        "BY": -1,
        "NC": -1,
        "ND": -1,
        "SA": -1,
        "provenance": {
            "handler": 'Wiley', # name of plugin which processed this record
            "handler_version": '0.2', # version of plugin which processed this record
            "category": "page_scrape", # category is page_scrape
            "description": 'License decided by scraping the resource at http://onlinelibrary.wiley.com/doi/10.1111/j.1365-2869.2012.01054.x/abstract and looking for the following license statement: "<span class="openAccess" title="You have full text access to this OnlineOpen article">You have full text access to this OnlineOpen article</span>".', # description is a long string
            "agent": config.agent, # agent is from configuration
            "source": "http://onlinelibrary.wiley.com/doi/10.1111/j.1365-2869.2012.01054.x/abstract", # source is the url where we look this record up
            "date": -1 # date is not null (but we don't know the exact value)
        }
    },

    # this case should be matched by the flat license index, not a publisher config
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "fnbeh.2013.00049.html"):
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
            "handler": 'generic_string_matcher', # name of plugin which processed this record
            "handler_version": '0.2', # version of plugin which processed this record
            "category": "page_scrape", # category is page_scrape
            "description": 'License decided by scraping the resource at http://journal.frontiersin.org/Journal/10.3389/fnbeh.2013.00049/full and looking for the following license statement: "This is an open-access article distributed under the terms of the <a href="http://creativecommons.org/licenses/by/3.0/" target="_blank">Creative Commons Attribution License</a>".', # description is a long string
            "agent": config.agent, # agent is from configuration
            "source": "http://journal.frontiersin.org/Journal/10.3389/fnbeh.2013.00049/full", # source is the url where we look this record up
            "date": -1 # date is not null (but we don't know the exact value)
        }
    },

    # This case should not be matched - the statement exists in the flat license index,
    # but the PLOS config should assert it will handle the case, therefore the flat
    # license index should never be used.
    # NOTE: none of the values will actually get tested as no license object will be created
    # Testing the unknown license is the job of the workflow tests, not this test.
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "pone.0037743.html"):
    {
        "id": None,            # there should be no id field
        "version": None,
        "type": "failed-to-obtain-license",
        "error_message": "unable to detect licence",
        "url": config.unknown_url,
        "jurisdiction": None,
        "open_access": False,
        "BY": None,
        "NC": None,
        "ND": None,
        "SA": None,
        "provenance": {
            "handler": 'oag', # name of plugin which processed this record
            "handler_version": '0.2', # version of plugin which processed this record
            "description": 'a plugin ran and failed to detect a license for this record.  This entry records that the license is therefore unknown', # description is a long string
            "agent": config.agent,
            "source": "http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0037743",
            "category": "failure",
            "date": -1 # date is not null (but we don't know the exact value)
        }
    },

    # just for testing whether a completely bogus one fails correctly, with the right handler and so on
    # NOTE: none of the values will actually get tested as no license object will be created
    # Testing the unknown license is the job of the workflow tests, not this test.
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "fail_please.txt"):
    {
        "id": None,            # there should be no id field
        "version": None,
        "type": "failed-to-obtain-license",
        "error_message": "unable to detect licence",
        "url": config.unknown_url,
        "jurisdiction": None,
        "open_access": False,
        "BY": None,
        "NC": None,
        "ND": None,
        "SA": None,
        "provenance": {
            "handler": 'oag',
            "handler_version": '0.2',
            "description": 'a plugin ran and failed to detect a license for this record.  This entry records that the license is therefore unknown', # description is a long string
            "agent": config.agent,
            "source": "",
            "category": "failure",

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

    return resp

class TestProvider(TestCase):

    def setUp(self):
        # need to remove the current publishers and license statements for
        # the duration of testing
        self.old_publishers = models.Publisher.all()
        self.old_license_statements = models.LicenseStatement.all()
        models.Publisher.delete_all()
        models.LicenseStatement.delete_all()

        p = models.Publisher()
        p.publisher_name = 'PLOS'
        p.journal_urls = ['http://www.plosone.org']
        p.licenses =\
        [
            {
                "license_type":"cc-by",
                "version":"",
                "example_doi":"doi:10.1371/journal.pone.0031314",
                "license_statement":"This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited."
            }
        ]
        p.save()
        
        p2 = models.Publisher()
        p2.publisher_name = 'Wiley'
        p2.journal_urls = ['http://onlinelibrary.wiley.com']
        p2.licenses =\
        [
            {
                "license_type":"free-to-read",
                "version":"",
                "example_doi":"doi:10.1111/j.1365-2869.2012.01054.x",
                "license_statement":"""<span class="openAccess" title="You have full text access to this OnlineOpen article">You have full text access to this OnlineOpen article</span>"""
            }
        ]
        p2.save()

        lic1 = models.LicenseStatement()
        lic1.license_type = 'cc-zero'
        lic1.version = ''
        lic1.example_doi = '10.1371/journal.pone.0037743'
        lic1.license_statement = 'This is an open-access article, free of all copyright, and may be freely reproduced, distributed, transmitted, modified, built upon, or otherwise used by anyone for any lawful purpose. The work is made available under the Creative Commons CC0 public domain dedication.'
        lic1.save()
        
        lic2 = models.LicenseStatement()
        lic2.license_type = 'cc-by'
        lic2.version = '3.0'
        lic2.example_doi = '10.3389/fnbeh.2013.00049'
        lic2.license_statement = 'This is an open-access article distributed under the terms of the <a href="http://creativecommons.org/licenses/by/3.0/" target="_blank">Creative Commons Attribution License</a>'
        lic2.save()

        self.test_publishers = [p, p2]
        self.test_license_statements = [lic1, lic2]

        models.Publisher.refresh()
        models.LicenseStatement.refresh()
        time.sleep(2)  # give the index a chance to perform the refresh

        # no live http connections inside the tests
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        self.old_get = requests.get
        requests.get = mock_get
        
    def tearDown(self):
        global CURRENT_REQUEST
        CURRENT_REQUEST = None
        requests.get = self.old_get

        # delete the test publishers and license statements
        for thing in self.test_publishers + self.test_license_statements:
            thing.delete()

        # restore the publisher and license statement records as they were
        for thing in self.old_publishers + self.old_license_statements:
            thing.save(do_not_timestamp=True)

        time.sleep(2)  # give the index time to catch up with the newly restored statements
        # otherwise the next setUp will only save 1 (or a few) of the license statements
        # before deleting them all


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
            detect_should_fail = False
            if comparison.get('type') == 'failed-to-obtain-license':
                detect_should_fail = True
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
            if not detect_should_fail:
                assert "license" in record['bibjson'], 'While testing with ' + path
                assert record['bibjson']['license'] is not None
                assert len(record['bibjson']['license']) == 1  # only 1 license was detected
            else:
                assert not "license" in record['bibjson'], 'While testing with ' + path
                return
            
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
                    assert key not in licence or licence.get(key) == "", ('While testing with ' + path, (key, value), licence.get(key))
                elif value == -1:
                    # the resulting object MUST have the key
                    assert key in licence, ('While testing with ' + path, (key, value), licence.get(key))
                else:
                    # the resulting object must match the comparison object
                    assert value == licence.get(key), ('While testing with ' + path, (key, value), licence.get(key))
            
            prov = licence.get("provenance", {})
            for key, value in comparison.get("provenance", {}).iteritems():
                if value is None:
                    # the resulting object MUST NOT have the key
                    assert key not in prov or prov.get(key) == "", ('While testing with ' + path, (key, value), prov.get(key))
                elif value == -1:
                    # the resulting object MUST have the key
                    assert key in prov, ('While testing with ' + path, (key, value), prov.get(key))
                else:
                    # the resulting object must match the comparison object
                    assert value == prov.get(key), ('While testing with ' + path, (key, value), prov.get(key))
