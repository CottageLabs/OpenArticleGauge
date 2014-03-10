from openarticlegauge import plugin

class mock_doi_canon(plugin.Plugin):
    _short_name="mock_doi"
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
    _short_name="mock_pmid"
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
