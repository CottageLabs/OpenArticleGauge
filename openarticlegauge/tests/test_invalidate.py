# NOTE: this is an integration test - it requires elastic search to be up and configured
#
# NOTE: this test uses time.sleep to try to give elastic search enough time to action the requests
# sent to it.  Sometimes these requests may fail to be ready in time, and the test will
# erroneously return as failed - you need to check that this isn't the case before getting
# too concerned with whether your test is working or not

from unittest import TestCase

from openarticlegauge import models, invalidate, config
import time

# run this if you want to test the migrate script
def generate_migrate_test():
    records = []
    
    # a few records missing the handler and version
    records.append(generate_record("111", [("failed-to-obtain-license", None, None)]))
    records.append(generate_record("222", [("failed-to-obtain-license", None, None)]))
    records.append(generate_record("333", [("failed-to-obtain-license", None, None)]))
    records.append(generate_record("444", [("failed-to-obtain-license", None, None)]))
    
    # a few properly created records
    records.append(generate_record("555", [("cc-by", "plugin_a", "1.0")]))
    records.append(generate_record("666", [("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("777", [("cc-by", "plugin_b", "1.0")]))
    records.append(generate_record("888", [("cc-by", "plugin_b", "2.0")]))

    # a few combos
    records.append(generate_record("141414", [("failed-to-obtain-license", None, None), ("cc-by", "plugin_a", "1.0")]))
    records.append(generate_record("151515", [("failed-to-obtain-license", None, None), ("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("161616", [("failed-to-obtain-license", None, None), ("cc-by", "plugin_b", "1.0")]))
    records.append(generate_record("171717", [("failed-to-obtain-license", None, None), ("cc-by", "plugin_b", "2.0")]))
    
    for bj in records:
        models.Record.store(bj)

def generate_records():
    records = []
    
    # record with no licence
    records.append(generate_record("000", []))
    
    # unknown licence for oag0.0, plugin_a1.0, plugin_a2.0, plugin_b1.0, plugin_c2.0
    records.append(generate_record("111", [("failed-to-obtain-license", "plugin_a", "1.0")]))
    records.append(generate_record("222", [("failed-to-obtain-license", "plugin_a", "2.0")]))
    records.append(generate_record("333", [("failed-to-obtain-license", "plugin_b", "1.0")]))
    records.append(generate_record("444", [("failed-to-obtain-license", "plugin_b", "2.0")]))
    records.append(generate_record("555", [("failed-to-obtain-license", "oag", "0.0")]))
    
    # cc-by for plugin_a1.0, plugin_a2.0, plugin_b1.0, plugin_c2.0
    records.append(generate_record("666", [("cc-by", "plugin_a", "1.0")]))
    records.append(generate_record("777", [("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("888", [("cc-by", "plugin_b", "1.0")]))
    records.append(generate_record("999", [("cc-by", "plugin_b", "2.0")]))
    
    # cc0 for plugin_a1.0, plugin_a2.0, plugin_b1.0, plugin_c2.0
    records.append(generate_record("101010", [("cc0", "plugin_a", "1.0")]))
    records.append(generate_record("111111", [("cc0", "plugin_a", "2.0")]))
    records.append(generate_record("121212", [("cc0", "plugin_b", "1.0")]))
    records.append(generate_record("131313", [("cc0", "plugin_b", "2.0")]))
    
    # unknown licence for oag0.0 + cc-by for plugin_a1.0, plugin_a2.0, plugin_b1.0, plugin_c2.0
    records.append(generate_record("141414", [("failed-to-obtain-license", "oag", "0.0"), ("cc-by", "plugin_a", "1.0")]))
    records.append(generate_record("151515", [("failed-to-obtain-license", "oag", "0.0"), ("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("161616", [("failed-to-obtain-license", "oag", "0.0"), ("cc-by", "plugin_b", "1.0")]))
    records.append(generate_record("171717", [("failed-to-obtain-license", "oag", "0.0"), ("cc-by", "plugin_b", "2.0")]))
    
    # unknown licence for plugin_a1.0 + cc-by, cc0 licence for plugin_a2.0
    records.append(generate_record("181818", [("failed-to-obtain-license", "plugin_a", "1.0"), ("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("191919", [("failed-to-obtain-license", "plugin_a", "1.0"), ("cc0", "plugin_a", "2.0")]))
    
    # unknown licence for plugin_b1.0 + cc-by, cc0 licence for plugin_b2.0
    records.append(generate_record("202020", [("failed-to-obtain-license", "plugin_b", "1.0"), ("cc-by", "plugin_b", "2.0")]))
    records.append(generate_record("212121", [("failed-to-obtain-license", "plugin_b", "1.0"), ("cc0", "plugin_b", "2.0")]))
    
    # cc-by licence for plugin_a1.0 + cc-by, cc0 licence for plugin_a2.0
    records.append(generate_record("222222", [("cc-by", "plugin_a", "1.0"), ("cc-by", "plugin_a", "2.0")]))
    records.append(generate_record("232323", [("cc-by", "plugin_a", "1.0"), ("cc0", "plugin_a", "2.0")]))
    
    # cc-by licence for plugin_b1.0 + cc-by, cc0 licence for plugin_b2.0
    records.append(generate_record("242424", [("cc-by", "plugin_b", "1.0"), ("cc-by", "plugin_b", "2.0")]))
    records.append(generate_record("252525", [("cc-by", "plugin_b", "1.0"), ("cc0", "plugin_b", "2.0")]))
    
    return records

def generate_record(id, licence_tup):
    record = {
        "id" : id,
        "identifier" : [{"id" : id, "canonical" : id}],
        "license" : []
    }
    
    for licence_type, handler, version in licence_tup:
        record["license"].append({
            "type" : licence_type,
            "provenance" : {
                "handler" : handler,
                "handler_version" : version
            }
        })
    return record

def compare(ids, length):
    for i in ids:
        obj = models.Record.pull(i)
        assert len(obj.data['license']) == length

bibjson_records = generate_records()

class TestInvalidate(TestCase):

    def setUp(self):
        self.buffer = config.BUFFERING
        config.BUFFERING = False
        # load all of the bibjson objects into the index
        for bj in bibjson_records:
            models.Record.store(bj)
            
        # set a page size which requires all query results to be paged (or at least, when there is more than one result)
        self.old_page_size = invalidate.ES_PAGE_SIZE
        invalidate.ES_PAGE_SIZE = 1
        time.sleep(2) # need to wait to give ES a chance to index the data
        
    def tearDown(self):
        config.BUFFERING = self.buffer
        
        # remove all of the bibjson objects we loaded into the index
        for bj in bibjson_records:
            r = models.Record(**bj)
            r.delete()
        invalidate.ES_PAGE_SIZE = self.old_page_size
        
    def test_01_unknown_all_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", reporter=invalidate.stdout_reporter)
        
        # 0 - 5 should have no licence
        compare(["000", "111", "222", "333", "444", "555"], 0)
        
        # 6 - 21 should have 1 licence
        compare(["666", "777", "888", "999", "101010", "111111", "121212", "131313", "141414", "151515", "161616", "171717", "181818", "191919", "202020", "212121"], 1)
        
        # 22 - 25 should still have two licences
        compare(["222222", "232323", "242424", "252525"], 2)
    
    def test_02_unknown_one_plugin_any_version(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", handler="plugin_a", reporter=invalidate.stdout_reporter)
        
        # 0 - 2 should have no licence
        compare(["000", "111", "222"], 0)
        
        # 3 - 13 and 18 - 19 should have 1 licence
        compare(["333", "444", "555", "666", "777", "888", "999", "101010", "111111", "121212", "131313", "181818", "191919"], 1)
        
        # 14 - 17 and 20 - 25 should still have two licences
        compare(["141414", "151515", "161616", "171717", "202020", "212121", "222222", "232323", "242424", "252525"], 2)
    
    def test_03_unknown_one_plugin_one_version(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("failed-to-obtain-license", handler="plugin_a", handler_version="1.0", reporter=invalidate.stdout_reporter)
        
        # 0 - 1 should have no licence
        compare(["000", "111"], 0)
        
        # 2 - 13, 18, 19 should have 1 licence
        compare(["222", "333", "444", "555", "666", "777", "888", "999", "101010", "111111", "121212", "131313", "181818", "191919"], 1)
        
        # 14 - 17, 20 - 25 should still have two licences
        compare(["141414", "151515", "161616", "171717", "202020", "212121", "222222", "232323", "242424", "252525"], 2)
    
    def test_04_known_all_plugins(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("cc0", reporter=invalidate.stdout_reporter)
        
        # 0, and 10 - 13 should have no licence
        compare(["000", "101010", "111111", "121212", "131313"], 0)
        
        # 2 - 9, 19, 21, 23, 25 should have 1 licence
        compare(["111", "222", "333", "444", "555", "666", "777", "888", "999", "191919", "212121", "232323", "252525"], 1)
        
        # 14 - 18, 20, 22, 24 should still have two licences
        compare(["141414", "151515", "161616", "171717", "181818", "202020", "222222", "242424"], 2)
    
    def test_05_known_one_plugin_all_versions(self):
        # invalidate all failed-to-obtain-license licences, irrespective of version or plugin
        invalidate.invalidate_license("cc0", handler="plugin_b", reporter=invalidate.stdout_reporter)
        
        # 0, 12 - 13 should have no licence
        compare(["000", "121212", "131313"], 0)
        
        # 1 - 11, 21, 25 should have 1 licence
        compare(["111", "222", "333", "444", "555", "666", "777", "888", "999", "101010", "111111", "212121", "252525"], 1)
        
        # 14 - 20, 22 - 24 should still have two licences
        compare(["141414", "151515", "161616", "171717", "181818", "191919", "202020", "222222", "232323", "242424"], 2)
        
    def test_06_known_all_plugins(self):
        invalidate.invalidate_license("cc0", handler="plugin_b", handler_version="2.0", reporter=invalidate.stdout_reporter)
        
        # 0, 13 should have no licence
        compare(["000", "131313"], 0)
        
        # 1 - 12, 21, 25 should have 1 licence
        compare(["111", "222", "333", "444", "555", "666", "777", "888", "999", "101010", "111111", "121212", "212121", "252525"], 1)
        
        # 14 - 20, 22 - 24 should still have two licences
        compare(["141414", "151515", "161616", "171717", "181818", "191919", "202020", "222222", "232323", "242424"], 2)
    
    def test_07_by_query_all(self):
        query = {
            "query" : {
                "match_all" : {}
            }
        }
        
        # invalidate all cc-by from plugin_b 2.0
        invalidate.invalidate_license_by_query(query, license_type="cc-by", handler="plugin_b", handler_version="2.0")
        
        # 0, 9 should have no licence
        compare(["000", "999"], 0)
        
        # 1 - 8, 10 - 13, 17, 20, 24 should have 1 licence
        compare(["111", "222", "333", "444", "555", "666", "777", "888", "101010", "111111", "121212", "131313", "171717", "202020", "242424"], 1)
        
        # 14 - 16, 18, 19, 21 - 23, 25 should still have two licences
        compare(["141414", "151515", "161616", "181818", "191919", "212121", "222222", "232323", "252525"], 2)

    def test_08_by_query_specific(self):
        query = {
            "query" : {
                "bool" : {
                    "must" : [
                        {"term" : {"license.type.exact" : "cc-by"}},
                        {"term" : {"license.provenance.handler.exact" : "plugin_a"}},
                        {"term" : {"license.provenance.handler_version.exact" : "1.0"}}
                    ]
                }
            }
        }
        
        # invalidate all cc-by from plugin_1 1.0
        invalidate.invalidate_license_by_query(query, license_type="cc-by", handler="plugin_a", handler_version="1.0")
        
        # 0, 6 should have no licence
        compare(["000", "666"], 0)
        
        # 1 - 5, 7 - 14, 22, 23 should have 1 licence
        compare(["111", "222", "333", "444", "555", "777", "888", "999", "101010", "111111", "121212", "131313", "141414", "222222", "232323"], 1)
        
        # 15 - 21, 24, 25 should still have two licences
        compare(["151515", "161616", "171717", "181818", "191919", "202020", "212121", "242424", "252525"], 2)
    
    def test_09_by_query_handler_only(self):
        query = {
            "query" : {
                "bool" : {
                    "must" : [
                        {"term" : {"license.type.exact" : "cc-by"}},
                        {"term" : {"license.provenance.handler.exact" : "plugin_a"}},
                        {"term" : {"license.provenance.handler_version.exact" : "1.0"}}
                    ]
                }
            }
        }
        
        # invalidate all cc-by from plugin_1 1.0
        invalidate.invalidate_license_by_query(query, handler="plugin_a")
        
        # 0, 6, 18, 22, 23 should have no licence
        compare(["000", "666", "181818", "222222", "232323"], 0)
        
        # 1 - 5, 7 - 14 should have 1 licence
        compare(["111", "222", "333", "444", "555", "777", "888", "999", "101010", "111111", "121212", "131313", "141414"], 1)
        
        # 15 - 17, 19 - 21, 24, 25 should still have two licences
        compare(["151515", "161616", "171717", "191919", "202020", "212121", "242424", "252525"], 2)
    




































