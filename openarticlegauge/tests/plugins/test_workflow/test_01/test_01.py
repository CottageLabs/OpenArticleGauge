from openarticlegauge import plugin, models

class mock_doi_type(plugin.Plugin):
    _short_name="mock_doi"
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
    _short_name="mock_pmid"
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
