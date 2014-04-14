from unittest import TestCase

from openarticlegauge.plugins.oup import OUPPlugin
from openarticlegauge import config, models

keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_01_oup_supports_success(self):
        oup = OUPPlugin()
        test_urls = ["http://www.oxfordjournals.org/983242", "http://chemistry.oxfordjournals.org/2987433",
        			 "http://schizophreniabulletin.oxfordjournals.org/content/40/1/169",
                        "https://www.biology.oxfordjournals.org/jsafkjsaf"]
        for url in test_urls:
            assert oup.supports({"url" : [url]})
        
    def test_02_oup_supports_fail(self):
        oup = OUPPlugin()
        test_urls = ["http://www.plosone.org/", "www.biomedcentral.com", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not oup.supports({"url" : [url]})

    def test_03_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://bioinformatics.oxfordjournals.org/content/28/22/2898']
        record = models.MessageObject(record=record)

        oup = OUPPlugin()
        oup.license_detect(record)

        record = record.record
        
        # just barebones checks to make sure the license and provenance objects
        # exist in the first place so the handler fields can be checked
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert 'provenance' in record['bibjson']['license'][-1]

        assert 'handler' in record['bibjson']['license'][-1]['provenance']
        assert record['bibjson']['license'][-1]['provenance']['handler'] == 'oup' 
        assert record['bibjson']['license'][-1]['provenance']['handler_version'] == '0.1'
    
    def test_04_oup_standard_OA_license_example1(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://bioinformatics.oxfordjournals.org/content/28/22/2898']
        record = models.MessageObject(record=record)

        oup = OUPPlugin()
        oup.license_detect(record)

        record = record.record

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-by'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the OUP plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by/3.0/'

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' \
        + "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/)," \
        + "\n" + ' '*21 + 'which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.".'

    def test_04_oup_standard_OA_license_example2(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://nar.oxfordjournals.org/content/40/21/10668']
        record = models.MessageObject(record=record)
        
        oup = OUPPlugin()
        oup.license_detect(record)
        
        record = record.record
        
        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-by'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the OUP plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by/3.0/'

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' \
        + "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/)," \
        + "\n" + ' '*21 + 'which permits unrestricted, distribution, and reproduction in any medium, provided the original work is properly cited.".'

    def test_05_oup_OA_NC_license(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://nar.oxfordjournals.org/content/40/21/10832']
        record = models.MessageObject(record=record)
        
        oup = OUPPlugin()
        oup.license_detect(record)

        record = record.record
        
        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-nc'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert not record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the OUP plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by-nc/3.0'

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' \
        + "This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0)," \
        + "\n" + ' '*21 + "which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is" \
        + "\n" + ' '*21 + 'properly cited.".'
        
    def test_06_oup_OA_NC_license2(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://schizophreniabulletin.oxfordjournals.org/content/40/1/169']
        record = models.MessageObject(record=record)
        
        oup = OUPPlugin()
        oup.license_detect(record)

        record = record.record
        
        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'cc-nc'
        assert record['bibjson']['license'][-1]['version'] == '3.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert not record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the OUP plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by-nc/3.0'

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'

        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at ' + record['provider']['url'][0] + ' and looking for the following license statement: "' \
        + "This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0/)," \
        + "\n" + ' '*21 + "which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is" \
        + "\n" + ' '*21 + 'properly cited.".'

