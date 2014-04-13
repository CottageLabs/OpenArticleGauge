from openarticlegauge import plugin
import re

class BMJPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    __desc__ = "Handles articles from the British Medical Journal Group"

    supported_url_format = '(http|https){0,1}://.+?\.bmj.com/.+'

    _license_mappings = [
            {"""This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits use, distribution, and reproduction in any medium, provided the original work is properly cited, the use is non commercial and is otherwise in compliance with the license. See: <a href="http://creativecommons.org/licenses/by-nc/2.0/">http://creativecommons.org/licenses/by-nc/2.0/</a>""":
                    {'type': 'cc-nc', 'version':'2.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by-nc/2.0/'}
            },
            {"""This is an Open Access article distributed in accordance with the terms of the Creative Commons Attribution (CC BY 3.0) license, which permits others to distribute, remix, adapt and build upon this work, for commercial use, provided the original work is properly cited. See: <a href="http://creativecommons.org/licenses/by/3.0/">http://creativecommons.org/licenses/by/3.0/</a>""":
                    {'type': 'cc-by', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/3.0/'}
            },
            {"""This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits use, distribution, and reproduction in any medium, provided the original work is properly cited, the use is non commercial and is otherwise in compliance with the license. See: <a href="http://creativecommons.org/licenses/by-nc/3.0/">http://creativecommons.org/licenses/by-nc/3.0/</a>""":
                    {'type': 'cc-nc', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by-nc/3.0'}
            }
        ]

    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }

    def supports(self, provider):
        """
        Does the page_license plugin support this provider
        """
        
        for url in provider.get("url", []):
            if self.supports_url(url):
                return True

        return False

    def supports_url(self, url):
        if re.match(self.supported_url_format, url):
            return True
        return False
    
    def license_detect(self, record):
        """
        To respond to the provider identifier: *.bmj.com
        
        This should determine the licence conditions of the BMJ article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # licensing statements to look for on this publisher's pages
        # take the form of {statement: meaning}
        # where meaning['type'] identifies the license (see licenses.py)
        # and meaning['version'] identifies the license version (if available)
        lic_statements = self._license_mappings
        
        for url in record.provider_urls:
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)

    def get_description(self, plugin_name):
        pd = super(BMJPlugin, self).get_description(plugin_name)
        pd.provider_support = "Supports urls which match the regular expression: " + self.supported_url_format
        return pd





