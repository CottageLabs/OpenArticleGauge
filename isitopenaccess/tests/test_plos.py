from unittest import TestCase

from isitopenaccess.plugins import plos
from isitopenaccess import config

keys_in_license = ['provenance', 'description', 'type', 'title', 'url',
    'jurisdiction', 'open_access', 'BY', 'NC', 'SA', 'ND']

keys_in_provenance = ['date', 'agent', 'source', 'category', 'description']

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass

    def test_01_plos_OGL_OA_example1(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = 'http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089'

        plos.page_license(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'] for key in keys_in_license)

        assert all (key in record['bibjson']['license']['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license']['type'] == 'uk-ogl'
        assert record['bibjson']['license']['version'] == ''
        assert 'id' not in record['bibjson']['license'] # should not have "id" - due to bibserver
        assert not record['bibjson']['license']['jurisdiction']
        assert record['bibjson']['license']['open_access']
        assert record['bibjson']['license']['BY']
        assert not record['bibjson']['license']['NC']
        assert not record['bibjson']['license']['SA']
        assert not record['bibjson']['license']['ND']

        assert record['bibjson']['license']['provenance']['agent'] == config.agent
        assert record['bibjson']['license']['provenance']['source'] == record['provider']['url']
        assert record['bibjson']['license']['provenance']['date']
        assert record['bibjson']['license']['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license']['provenance']['description'] == 'License decided by scraping the resource at http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0035089 and looking for the following license statement: "This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.".'

    def test_02_plos_standard_OA_example1(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = 'http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406'

        plos.page_license(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'] for key in keys_in_license)

        assert all (key in record['bibjson']['license']['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license']['type'] == 'cc-by'
        assert record['bibjson']['license']['version'] == ''
        assert 'id' not in record['bibjson']['license'] # should not have "id" - due to bibserver
        assert not record['bibjson']['license']['jurisdiction']
        assert record['bibjson']['license']['open_access']
        assert record['bibjson']['license']['BY']
        assert not record['bibjson']['license']['NC']
        assert not record['bibjson']['license']['SA']
        assert not record['bibjson']['license']['ND']

        assert record['bibjson']['license']['provenance']['agent'] == config.agent
        assert record['bibjson']['license']['provenance']['source'] == record['provider']['url']
        assert record['bibjson']['license']['provenance']['date']
        assert record['bibjson']['license']['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license']['provenance']['description'] == 'License decided by scraping the resource at http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001406 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.".'

    def test_03_plos_standard_OA_example2(self):
        record = {}
        record['bibjson'] = {}
        record['provider'] = {}
        record['provider']['url'] = 'http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461'

        plos.page_license(record)

        # check if all the important keys were created
        assert record['bibjson'].has_key('license')

        # NB: some examples may fail the 'url' test since the Open Definition
        # data we're using as the basis for our licenses dictionary does not
        # have 'url' for all licenses. Fix by modifying licenses.py - add the data.
        # TODO remove this "all" assertion - if it fails, doesn't say which key missing
        assert all (key in record['bibjson']['license'] for key in keys_in_license)

        assert all (key in record['bibjson']['license']['provenance'] for key in keys_in_provenance)

        # some content checks now
        assert record['bibjson']['license']['type'] == 'cc-by'
        assert record['bibjson']['license']['version'] == ''
        assert 'id' not in record['bibjson']['license'] # should not have "id" - due to bibserver
        assert not record['bibjson']['license']['jurisdiction']
        assert record['bibjson']['license']['open_access']
        assert record['bibjson']['license']['BY']
        assert not record['bibjson']['license']['NC']
        assert not record['bibjson']['license']['SA']
        assert not record['bibjson']['license']['ND']

        assert record['bibjson']['license']['provenance']['agent'] == config.agent
        assert record['bibjson']['license']['provenance']['source'] == record['provider']['url']
        assert record['bibjson']['license']['provenance']['date']
        assert record['bibjson']['license']['provenance']['category'] == 'page_scrape'
        assert record['bibjson']['license']['provenance']['description'] == 'License decided by scraping the resource at http://www.plosbiology.org/article/info%3Adoi%2F10.1371%2Fjournal.pbio.1001461 and looking for the following license statement: "This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.".'
