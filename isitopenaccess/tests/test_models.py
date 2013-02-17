from unittest import TestCase

from isitopenaccess.models import ResultSet
import json

class TestWorkflow(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_01_resultset_init(self):
        rs = ResultSet()
        assert rs.requested == 0
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
        
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = ResultSet(ids)
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
    
    def test_02_resultset_results(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : "http://www.hindawi.com/article",
                    "bibjson" : {"title" :  "my title"}
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 1
        assert len(rs.errors) == 0
        assert len(rs.processing) == 0
        
        bibjson = rs.results[0]
        assert bibjson.has_key("title")
        assert bibjson["title"] == "my title"
        assert bibjson.has_key("identifier")
        assert len(bibjson["identifier"]) == 1
        assert bibjson["identifier"][0].has_key("id")
        assert bibjson["identifier"][0].has_key("type")
        assert bibjson["identifier"][0].has_key("canonical")
        
    def test_03_resultset_errors(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : "http://www.hindawi.com/article",
                    "error" : "broken"
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 1
        assert len(rs.processing) == 0
        
        error = rs.errors[0]
        assert error.has_key("error")
        assert error["error"] == "broken"
        assert error.has_key("identifier")
        assert error["identifier"].has_key("id")
        
    def test_04_resultset_processing(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}]
        rs = ResultSet(ids)
        
        result = {
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : "http://www.hindawi.com/article",
                    "queued" : True
                 }
        rs.add_result_record(result)
        
        assert rs.requested == 3
        assert len(rs.results) == 0
        assert len(rs.errors) == 0
        assert len(rs.processing) == 1
        
        queued = rs.processing[0]
        assert queued.has_key("identifier")
        assert queued["identifier"].has_key("id")
    
    def test_05_resultset_mixed(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}, {"id" : "4"}]
        rs = ResultSet(ids)
        
        results = []
        results.append({
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : "http://www.hindawi.com/article",
                    "bibjson" : {"title" :  "my title"}
                 })
                 
        results.append({
                    "identifier" : {"id" : "2", "type" : "doi", "canonical" : "doi:2"},
                    "provider" : "http://www.hindawi.com/article",
                    "error" : "broken"
                 })
        
        results.append({
                    "identifier" : {"id" : "3", "type" : "doi", "canonical" : "doi:3"},
                    "provider" : "http://www.hindawi.com/article",
                    "queued" : True
                 })
        
        results.append({
                "identifier" : {"id" : "4", "type" : "doi", "canonical" : "doi:4"},
                "provider" : "http://www.hindawi.com/hello",
                "bibjson" : {"title" :  "another title"}
            })
            
        for result in results:
            rs.add_result_record(result)
    
        assert rs.requested == 4
        assert len(rs.results) == 2
        assert len(rs.errors) == 1
        assert len(rs.processing) == 1
        
        assert rs.results[0]['title'] in ["my title", "another title"]
        
    
    def test_06_resultset_json(self):
        ids = [{"id" : "1"}, {"id" : "2"}, {"id" : "3"}, {"id" : "4"}]
        rs = ResultSet(ids)
        
        results = []
        results.append({
                    "identifier" : {"id" : "1", "type" : "doi", "canonical" : "doi:1"},
                    "provider" : "http://www.hindawi.com/article",
                    "bibjson" : {"title" :  "my title"}
                 })
                 
        results.append({
                    "identifier" : {"id" : "2", "type" : "doi", "canonical" : "doi:2"},
                    "provider" : "http://www.hindawi.com/article",
                    "error" : "broken"
                 })
        
        results.append({
                    "identifier" : {"id" : "3", "type" : "doi", "canonical" : "doi:3"},
                    "provider" : "http://www.hindawi.com/article",
                    "queued" : True
                 })
        
        results.append({
                "identifier" : {"id" : "4", "type" : "doi", "canonical" : "doi:4"},
                "provider" : "http://www.hindawi.com/hello",
                "bibjson" : {"title" :  "another title"}
            })
            
        for result in results:
            rs.add_result_record(result)
            
        j = rs.json()
        obj = json.loads(j)
        
        assert obj['requested'] == 4
        assert len(obj['results']) == 2
        assert len(obj['errors']) == 1
        assert len(obj['processing']) == 1
        
        
