from unittest import TestCase

from openarticlegauge.plugins.cell_reports import CellReportsPlugin
from openarticlegauge import config, models

keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND', 'error_message', 'suggested_solution']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_01_name_and_version(self):
        """
        Take an example supported article and check just the handler fields
        """
        cell_reports = CellReportsPlugin()
        
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.cell.com/cell-reports/fulltext/S2211-1247%2812%2900426-3']
        record = models.MessageObject(record=record)
        
        cell_reports.license_detect(record)
        
        # for convenience, unwrap the record
        record = record.record
        
        # just barebones checks to make sure the license and provenance objects
        # exist in the first place so the handler fields can be checked
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert 'provenance' in record['bibjson']['license'][-1]

        assert 'handler' in record['bibjson']['license'][-1]['provenance']
        assert record['bibjson']['license'][-1]['provenance']['handler'] == 'cell_reports'
        assert record['bibjson']['license'][-1]['provenance']['handler_version'] == '0.1'


    def test_02_cell_reports_standard_OA_license(self):
        cell_reports = CellReportsPlugin()
        
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = ['http://www.cell.com/cell-reports/fulltext/S2211-1247%2812%2900426-3']
        record = models.MessageObject(record=record)
        
        cell_reports.license_detect(record)
        
        # for convenience, unwrap the record
        record = record.record
        
        # check if all the important keys were created
        assert record['bibjson'].has_key('license')
        assert record['bibjson']['license']

        assert all (key in record['bibjson']['license'][-1] for key in keys_in_license)

        assert all (key in record['bibjson']['license'][-1]['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license'][-1]['type'] == 'failed-to-obtain-license'
        assert not record['bibjson']['license'][-1]['version']
        assert 'id' not in record['bibjson']['license'][-1] # should not have "id" - due to bibserver
        assert not record['bibjson']['license'][-1]['jurisdiction']
        assert not record['bibjson']['license'][-1]['open_access']
        assert not record['bibjson']['license'][-1]['BY']
        assert not record['bibjson']['license'][-1]['NC']
        assert not record['bibjson']['license'][-1]['SA']
        assert not record['bibjson']['license'][-1]['ND']

        assert record['bibjson']['license'][-1]['error_message'] == cell_reports.fail_why
        assert record['bibjson']['license'][-1]['suggested_solution'] == cell_reports.fail_suggested_solution

        assert record['bibjson']['license'][-1]['provenance']['agent'] == config.agent
        assert record['bibjson']['license'][-1]['provenance']['source'] == record['provider']['url'][0]
        assert record['bibjson']['license'][-1]['provenance']['date']
        assert record['bibjson']['license'][-1]['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license'][-1]['provenance']['description'] == 'We have found it impossible or prohibitively difficult to decide what the license of this item is by scraping the resource at ' + record['provider']['url'][0] + '. See "error_message" in the "license" object for more information.'
