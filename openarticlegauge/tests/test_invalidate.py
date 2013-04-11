# NOTE: this is an integration test - it requires elastic search to be up and configured
#
# NOTE: this test uses time.sleep to try to give elastic search enough time to action the requests
# sent to it.  Sometimes these requests may fail to be ready in time, and the test will
# erroneously return as failed - you need to check that this isn't the case before getting
# too concerned with whether your test is working or not

from unittest import TestCase

from openarticlegauge import models, invalidate
import time

bibjson_records = [
    {
        "id" : "111",
        "license" : [
            {
                "type" : "failed-to-obtain-license",
                "provenance" : {
                    "handler" : "plugin_a",
                    "handler_version" :  "1.0"
                }
            },
            {
                "type" : "failed-to-obtain-license",
                "provenance" : {
                    "handler" : "plugin_a",
                    "handler_version" :  "1.0"
                }
            }
        ]
    },
    {
        "id" : "222",
        "license" : [
            {
                "type" : "failed-to-obtain-license",
                "provenance" : {
                    "handler" : "plugin_b",
                    "handler_version" :  "1.0"
                }
            },
            {
                "type" : "failed-to-obtain-license"
            }
        ]
    },
    {
        "id" : "333",
        "license" : [
            {
                "type" : "failed-to-obtain-license",
                "provenance" : {
                    "handler" : "plugin_a",
                    "handler_version" :  "1.1"
                }
            },
            {
                "type" : "cc0",
                "provenance" : {
                    "handler" : "plugin_a",
                    "handler_version" :  "1.1"
                }
            }
        ]
    },
    {
        "id" : "444",
        "license" : [{
            "type" : "failed-to-obtain-license",
            "provenance" : {
                "handler" : "plugin_b",
                "handler_version" :  "1.1"
            }
        }]
    },
    {
        "id" : "555",
        "license" : [{
            "type" : "cc0",
            "provenance" : {
                "handler" : "plugin_a",
                "handler_version" :  "1.0"
            }
        }]
    },
    {
        "id" : "666",
        "license" : [{
            "type" : "cc0",
            "provenance" : {
                "handler" : "plugin_b",
                "handler_version" :  "1.0"
            }
        }]
    },
    {
        "id" : "777",
        "license" : [{
            "type" : "cc0",
            "provenance" : {
                "handler" : "plugin_a",
                "handler_version" :  "1.1"
            }
        }]
    },
    {
        "id" : "888",
        "license" : [{
            "type" : "cc0",
            "provenance" : {
                "handler" : "plugin_b",
                "handler_version" :  "1.1"
            }
        }]
    },
]

class TestInvalidate(TestCase):

    def setUp(self):
        # load all of the bibjson objects into the index
        for bj in bibjson_records:
            models.Record.store(bj)
            
        # set a page size which requires all query results to be paged (or at least, when there is more than one result)
        self.old_page_size = invalidate.ES_PAGE_SIZE
        invalidate.ES_PAGE_SIZE = 1
        time.sleep(2) # need to wait to give ES a chance to index the data
        
    def tearDown(self):
        # remove all of the bibjson objects we loaded into the index
        for bj in bibjson_records:
            r = models.Record(**bj)
            r.delete()
        invalidate.ES_PAGE_SIZE = self.old_page_size
        
    def test_01_unknown_all_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 0
        assert len(two.data['license']) == 0
        assert len(three.data['license']) == 1
        assert len(four.data['license']) == 0
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 1
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 1
    
    def test_02_unknown_one_plugin_any_version(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", handler="plugin_a", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 0
        assert len(two.data['license']) == 2
        assert len(three.data['license']) == 1
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 1
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 1
    
    def test_03_unknown_one_plugin_one_version(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", handler="plugin_a", handler_version="1.0", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 0
        assert len(two.data['license']) == 2
        assert len(three.data['license']) == 2
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 1
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 1
    
    def test_04_known_all_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("cc0", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 2
        assert len(two.data['license']) == 2
        assert len(three.data['license']) == 1
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 0
        assert len(six.data['license']) == 0
        assert len(seven.data['license']) == 0
        assert len(eight.data['license']) == 0
    
    def test_05_known_one_plugin_all_versions(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("cc0", handler="plugin_b", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 2
        assert len(two.data['license']) == 2
        assert len(three.data['license']) == 2
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 0
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 0
        
    def test_06_known_all_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("cc0", handler="plugin_b", handler_version="1.1", reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 2
        assert len(two.data['license']) == 2
        assert len(three.data['license']) == 2
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 1
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 0
        
    def test_07_unknown_no_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", treat_none_as_missing=True, reporter=invalidate.stdout_reporter)
        
        one = models.Record.pull("111")
        two = models.Record.pull("222")
        three = models.Record.pull("333")
        four = models.Record.pull("444")
        five = models.Record.pull("555")
        six = models.Record.pull("666")
        seven = models.Record.pull("777")
        eight = models.Record.pull("888")
        
        assert len(one.data['license']) == 2
        assert len(two.data['license']) == 1
        assert len(three.data['license']) == 2
        assert len(four.data['license']) == 1
        assert len(five.data['license']) == 1
        assert len(six.data['license']) == 1
        assert len(seven.data['license']) == 1
        assert len(eight.data['license']) == 1
