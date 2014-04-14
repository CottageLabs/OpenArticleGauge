from openarticlegauge import plugin
import re

class OUPPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    __desc__ = "Handles articles from the Oxford University Press"

    supported_url_format = '(http|https){0,1}://.+?\.oxfordjournals.org/.+'

    _license_mappings = [
            {"This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),"
                    + "\n" + ' '*21 + "which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.":
                {'type': 'cc-by', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/3.0/'}
            },
            { # this license statement is the same as the one above, but somebody's missed out the "reuse" word after unrestricted
             "This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),"
                    + "\n" + ' '*21 + "which permits unrestricted, distribution, and reproduction in any medium, provided the original work is properly cited.":
                {'type': 'cc-by', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/3.0/'}
            },
            {"This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0),"
                    + "\n" + ' '*21 +  "which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is"
                    + "\n" + ' '*21 +  "properly cited.":
                {'type': 'cc-nc', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by-nc/3.0/'}
            },
            {"This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0/),"
                    + "\n" + ' '*21 +  "which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is"
                    + "\n" + ' '*21 +  "properly cited.":
                {'type': 'cc-nc', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by-nc/3.0/'}
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
        To respond to the provider identifier: *.oxfordjournals.org
        
        This should determine the licence conditions of the OUP article and populate
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
        pd = super(OUPPlugin, self).get_description(plugin_name)
        pd.provider_support = "Supports urls which match the regular expression: " + self.supported_url_format
        return pd





