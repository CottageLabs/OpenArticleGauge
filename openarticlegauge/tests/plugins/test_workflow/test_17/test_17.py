from openarticlegauge import plugin

class mock_detect_provider(plugin.Plugin):
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : ["doi"],
            "license_detect" : False
        }
    def detect_provider(self, record):
        record.add_provider_url("http://provider")

class mock_licence_plugin(plugin.Plugin):
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
        record.record['bibjson']['license'] = [{}]
        record.record['bibjson']['title'] = "mytitle"
