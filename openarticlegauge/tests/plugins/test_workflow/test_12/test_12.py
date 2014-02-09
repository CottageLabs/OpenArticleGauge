from openarticlegauge import plugin

class mock_unknown_licence_plugin(plugin.Plugin):
    __version__ = "1.0"
    _short_name = "test_workflow"
    
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }
    def supports(self, provider):
        return True
    def license_detect(self, record):
        record.record['bibjson'] = {}
