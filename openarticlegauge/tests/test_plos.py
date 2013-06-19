from unittest import TestCase

from openarticlegauge.plugins.plos import PLOSPlugin
from openarticlegauge import config

keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_01_plos_supports_success(self):
        plos = PLOSPlugin()
        test_urls = ["http://www.plosone.org/1234", "www.plosbiology.org/fakjsskjdaf", "https://www.plosmedicine.org/asdfdsafa",
                        "www.ploscompbiol.org", "www.plosgenetics.org", "www.plospathogens.org", "www.plosntds.org"]
        for url in test_urls:
            assert plos.supports({"url" : [url]})
        
    def test_02_plos_supports_fail(self):
        plos = PLOSPlugin()
        test_urls = ["http://www.biomedcentral.com/", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not plos.supports({"url" : [url]})

    def test_03_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089']

        plos = PLOSPlugin()
        plos.license_detect(record)

        # just barebones checks to make sure the license and provenance objects
        # exist in the first place so the handler fields can be checked
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert 'provenance' in record['bibjson']['license'][-1]

        assert 'handler' in record['bibjson']['license'][-1]['provenance']
        assert record['bibjson']['license'][-1]['provenance']['handler'] == 'plos', 'was actually: ' + record['bibjson']['license'][-1]['provenance']['handler']
        assert record['bibjson']['license'][-1]['provenance']['handler_version'] == '0.1'
    
    def test_04_plos_OGL_OA_example1(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089']

        plos = PLOSPlugin()
        plos.license_detect(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'uk-ogl'
        assert record['bibjson']['license'][-1]['version'] == ''
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089 and looking for the following license statement: "This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.".'

    def test_05_plos_standard_OA_example1(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406']

        plos = PLOSPlugin()
        plos.license_detect(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-by'
        assert record['bibjson']['license'][-1]['version'] == ''
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.".'

    def test_06_plos_standard_OA_example2(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461']
        
        plos = PLOSPlugin()
        plos.license_detect(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-by'
        assert record['bibjson']['license'][-1]['version'] == ''
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.".'

    def test_07_plos_public_domain_dedication(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0037743']

        plos = PLOSPlugin()
        plos.license_detect(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-zero'
        assert record['bibjson']['license'][-1]['version'] == ''
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert not record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0037743 and looking for the following license statement: "This is an open-access article, free of all copyright, and may be freely reproduced, distributed, transmitted, modified, built upon, or otherwise used by anyone for any lawful purpose. The work is made available under the Creative Commons CC0 public domain dedication.".'
