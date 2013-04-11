# FIXME: do we still need this test case, if test_provider_skeleton is working fine?

from unittest import TestCase

from openarticlegauge.plugins.bmc import BMCPlugin # TUTORIAL: change this to import *your* plugin
from openarticlegauge import config

# TUTORIAL: no need to modify any of this unless you added a key to the license info
keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class TestBasic(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    # TUTORIAL
    # Give some examples of dereferenced URL-s which you expect to work.
    # Dereferenced means NOT http://dx.doi.org/10.1186/1471-2164-13-425
    # but the result of the redirect from hitting that).
    def test_01_bmc_supports_success(self):
        test_urls = ["http://www.biomedcentral.com/983242"]
        bmc = BMCPlugin()
        for url in test_urls:
            assert bmc.supports({"url" : [url]})

    # TUTORIAL
    # Now give some examples of URL-s and strings that should not be
    # supported.        
    def test_02_bmc_supports_fail(self):
        test_urls = ["http://www.plosone.org/", "askjdfsakjdhfsa"]
        bmc = BMCPlugin()
        for url in test_urls:
            assert not bmc.supports({"url" : [url]})

    # TUTORIAL: Repeat success examples from above test. 
    def test_03_bmc_supports_url_success(self):
        test_urls = ["http://www.biomedcentral.com/983242"]
        bmc = BMCPlugin()
        for url in test_urls:
            assert bmc.supports_url(url)
    
    # TUTORIAL: Repeat failure examples from above test. 
    def test_04_bmc_supports_url_fail(self):
        bmc = BMCPlugin()
        test_urls = ["http://www.plosone.org/", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not bmc.supports_url(url)

    def test_05_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.biomedcentral.com/1471-2164/13/425']
        
        bmc = BMCPlugin()
        bmc.license_detect(record)

        # just barebones checks to make sure the license and provenance objects
        # exist in the first place so the handler fields can be checked
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert 'provenance' in record['bibjson']['license'][-1]

        assert 'handler' in record['bibjson']['license'][-1]['provenance']
        assert record['bibjson']['license'][-1]['provenance']['handler'] == bmc._short_name
        assert record['bibjson']['license'][-1]['provenance']['handler_version'] == bmc.__version__
    
    def test_06_bmc_standard_OA_license(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        
        # TUTORIAL
        # Again, you must provide a dereferenced URL here - that's what your
        # plugin will get!
        record['provider']['url'] = ['http://www.biomedcentral.com/1471-2164/13/425']

        bmc = BMCPlugin()
        bmc.license_detect(record)

        # check if all the important keys were created
        
        # TUTORIAL: You don't need to modify any of these
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        # TUTORIAL: this is what you need to modify to make sure your plugin is
        # recording the right data. Essentially this should match whatever you put
        # into lic_statements in the plugin code and whatever you're expecting
        # for this particular resource.
        assert record['bibjson']['license'][-1]['type'] == 'cc-by'
        assert record['bibjson']['license'][-1]['version'] == '2.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by/2.0'

        # TUTORIAL: you don't need to touch the following tests, EXCEPT for
        # the last one - the human-readable provenance description.
        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        # TUTORIAL: This is what you need to change - this is the license
        # statement from lic_statements that you expect to have been present
        # on this resource's page.
        lic_statement = 'This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href=\'http://creativecommons.org/licenses/by/2.0\'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.' \
        
        # TUTORIAL: this is essentially some boilerplate text that you should not change
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' + lic_statement + '".'
