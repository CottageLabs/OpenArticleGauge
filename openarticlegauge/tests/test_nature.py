# FIXME: do we still need this test case, if test_provider_skeleton is working fine?

from unittest import TestCase

from openarticlegauge.plugins.nature import NaturePlugin # TUTORIAL: change this to import *your* plugin
from openarticlegauge import config, models

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
    def test_01_nature_supports_success(self):
        test_urls = ["http://www.nature.com/ncomms/journal/v1/n1/full/ncomms1007.html"]
        npg = NaturePlugin()
        for url in test_urls:
            assert npg.supports({"url" : [url]})

    # TUTORIAL
    # Now give some examples of URL-s and strings that should not be
    # supported.        
    def test_02_nature_supports_fail(self):
        test_urls = ["http://www.plosone.org/", "askjdfsakjdhfsa"]
        npg = NaturePlugin()
        for url in test_urls:
            assert not npg.supports({"url" : [url]})

    # TUTORIAL: Repeat success examples from above test. 
    def test_03_npg_supports_url_success(self):
        test_urls = ["http://www.nature.com/srep/2013/130415/srep01657/full/srep01657.html"]
        npg = NaturePlugin()
        for url in test_urls:
            assert npg.supports_url(url)
    
    # TUTORIAL: Repeat failure examples from above test. 
    def test_04_npg_supports_url_fail(self):
        npg = NaturePlugin()
        test_urls = ["http://www.biomedcentral.com/983242", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not npg.supports_url(url)

    def test_05_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.nature.com/srep/2013/130415/srep01657/full/srep01657.html']
        record = models.MessageObject(record=record)
        
        npg = NaturePlugin()
        npg.license_detect(record)

        record = record.record
        
        # just barebones checks to make sure the license and provenance objects
        # exist in the first place so the handler fields can be checked
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert 'provenance' in record['bibjson']['license'][-1]

        assert 'handler' in record['bibjson']['license'][-1]['provenance']
        assert record['bibjson']['license'][-1]['provenance']['handler'] == 'nature' 
        assert record['bibjson']['license'][-1]['provenance']['handler_version'] == '0.1'
    
    def test_06_npg_ccncsa_license(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        
        # TUTORIAL
        # Again, you must provide a dereferenced URL here - that's what your
        # plugin will get!
        record['provider']['url'] = ['http://www.nature.com/srep/2013/130415/srep01657/full/srep01657.html']
        record = models.MessageObject(record=record)
        
        npg = NaturePlugin()
        npg.license_detect(record)

        # check if all the important keys were created
        record = record.record
        
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
        assert record['bibjson']['license'][-1]['type'] == 'cc-nc-sa'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert not record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert record['bibjson']['license'][-1]['NC']
        assert record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by-nc-sa/3.0/'

        # TUTORIAL: you don't need to touch the following tests, EXCEPT for
        # the last one - the human-readable provenance description.
        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        # TUTORIAL: This is what you need to change - this is the license
        # statement from lic_statements that you expect to have been present
        # on this resource's page.
        lic_statement = 'This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by-nc-sa/3.0/">http://creativecommons.org/licenses/by-nc-sa/3.0/</a>' \
        
        # TUTORIAL: this is essentially some boilerplate text that you should not change
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' + lic_statement + '".'
        
    def test_07_npg_ccncnd_license(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        
        # TUTORIAL
        # Again, you must provide a dereferenced URL here - that's what your
        # plugin will get!
        record['provider']['url'] = ['http://www.nature.com/ncomms/journal/v4/n4/full/ncomms2674.html']
        record = models.MessageObject(record=record)
        
        npg = NaturePlugin()
        npg.license_detect(record)

        # check if all the important keys were created
        record = record.record
        
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
        assert record['bibjson']['license'][-1]['type'] == 'cc-nc-nd'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert not record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert record['bibjson']['license'][-1]['ND']
        # In this case we also expect the plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by-nc-nd/3.0/'

        # TUTORIAL: you don't need to touch the following tests, EXCEPT for
        # the last one - the human-readable provenance description.
        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        # TUTORIAL: This is what you need to change - this is the license
        # statement from lic_statements that you expect to have been present
        # on this resource's page.
        lic_statement = 'This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by-nc-nd/3.0/">http://creativecommons.org/licenses/by-nc-nd/3.0/</a>' \
        
        # TUTORIAL: this is essentially some boilerplate text that you should not change
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' + lic_statement + '".'
        
    def test_08_npg_ccby_license(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        
        # TUTORIAL
        # Again, you must provide a dereferenced URL here - that's what your
        # plugin will get!
        record['provider']['url'] = ['http://www.nature.com/srep/2013/130129/srep01154/full/srep01154.html']
        record = models.MessageObject(record=record)
        
        npg = NaturePlugin()
        npg.license_detect(record)

        # check if all the important keys were created
        record = record.record
        
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
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by/3.0/'

        # TUTORIAL: you don't need to touch the following tests, EXCEPT for
        # the last one - the human-readable provenance description.
        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        # TUTORIAL: This is what you need to change - this is the license
        # statement from lic_statements that you expect to have been present
        # on this resource's page.
        lic_statement = 'This work is licensed under a Creative Commons Attribution 3.0 Unported License. To view a copy of this license, visit  <a href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>' \
        
        # TUTORIAL: this is essentially some boilerplate text that you should not change
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' + lic_statement + '".'
        
