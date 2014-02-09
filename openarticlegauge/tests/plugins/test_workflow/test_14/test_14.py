from openarticlegauge import plugin

class mock_doi_type(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : True,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : False
        }
    def type_detect_verify(self, record):
        if record.id.startswith("10"):
            record.identifier_type = "doi"
            return
        if record.identifier_type == "doi":
            raise models.LookupException("oi")
        
class mock_pmid_type(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : True,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : False
        }
    def type_detect_verify(self, record):
        if record.id == "12345678":
            record.identifier_type = "pmid"
            
class mock_doi_canon(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : ["doi"],
            "detect_provider" : [],
            "license_detect" : False
        }
    def canonicalise(self, record):
        if record.identifier_type == "doi":
            record.canonical = record.identifier_type + ":" + record.id
        
class mock_pmid_canon(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : ["pmid"],
            "detect_provider" : [],
            "license_detect" : False
        }
    def canonicalise(self, record):
        if record.identifier_type == "pmid":
            record.canonical = record.identifier_type + ":" + record.id
