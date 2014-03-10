from openarticlegauge import plugin

class mock_licence_plugin(plugin.Plugin):
    _short_name="mock"
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
