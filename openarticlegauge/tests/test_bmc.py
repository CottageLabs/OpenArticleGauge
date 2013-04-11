from unittest import TestCase
import requests

from openarticlegauge.plugins.bmc import BMCPlugin
from openarticlegauge import config

keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class MockResponse():
    def __init__(self, status):
        self.status_code = status
        self.text = None
        self.url = None

def get_unknown(url, *args, **kwargs):
    resp = MockResponse(200)
    resp.text = "some text"

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_bmc_supports_success(self):
        bmc = BMCPlugin()
        test_urls = ["http://www.biomedcentral.com/983242"]
        for url in test_urls:
            assert bmc.supports({"url" : [url]})
        
    def test_02_bmc_supports_fail(self):
        bmc = BMCPlugin()
        test_urls = ["http://www.plosone.org/", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not bmc.supports({"url" : [url]})
    
    def test_03_bmc_supports_url_success(self):
        bmc = BMCPlugin()
        test_urls = ["http://www.biomedcentral.com/983242"]
        for url in test_urls:
            assert bmc.supports_url(url)
    
    def test_04_bmc_supports_url_fail(self):
        bmc = BMCPlugin()
        test_urls = ["http://www.plosone.org/", "askjdfsakjdhfsa"]
        for url in test_urls:
            assert not bmc.supports_url(url)

    def test_05_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        bmc = BMCPlugin()
        
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.biomedcentral.com/1471-2164/13/425']

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
        bmc = BMCPlugin()
        
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.biomedcentral.com/1471-2164/13/425']

        bmc.license_detect(record)

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
        assert record['bibjson']['license'][-1]['version'] == '2.0'
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert record['bibjson']['license'][-1]['open_access']
        assert record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']
        # In this case we also expect the BMC plugin to overwrite the ['license']['url']
        # property with a more specific one from the license statement.
        assert record['bibjson']['license'][-1]['url'] == 'http://creativecommons.org/licenses/by/2.0'

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'License decided by scraping the resource at http://www.biomedcentral.com/1471-2164/13/425 and looking for the following license statement: "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href=\'http://creativecommons.org/licenses/by/2.0\'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.".'
    
    def test_07_unknown(self):
        old_get = requests.get
        requests.get = get_unknown
        bmc = BMCPlugin()
        
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://unknown']
        
        bmc.license_detect(record)

        # check if all the important keys were created
        assert "license" not in record['bibjson']
        
        requests.get = old_get
        
