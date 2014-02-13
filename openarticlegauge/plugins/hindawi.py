"""
This plugin handles Hindawi articles.
Hindawi publish from a single domain and use a consistent format for licenses
so this one should be relatively straightforward.
"""

from openarticlegauge import plugin

class HindawiPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    # Specified without the schema (protocol - e.g. "http://") part.
    base_urls = ["www.hindawi.com"]
    # so if the http://www.hindawi.com/journals/ecam/2013/429706/ URL comes in,
    # it should be supported.
    
    def capabilities(self):
        return {
            "type_detect_verify" : False,
            "canonicalise" : [],
            "detect_provider" : [],
            "license_detect" : True
        }
    
    def supports(self, provider):
        """
        Does this plugin support this provider
        """
        
        work_on = self.clean_urls(provider.get("url", []))

        for url in work_on:
            if self.supports_url(url):
                return True

        return False

    def supports_url(self, url):
        """
        Same as the supports() function but answers the question for a single URL.
        """
        for bu in self.base_urls:
            if self.clean_url(url).startswith(bu):
                return True
        return False

    def license_detect(self, record):
        
        """
        To respond to the provider identifier: http://www.hindawi.com
        
        This should determine the licence conditions of the Hindawi article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """
        
        lic_statements = [
            {'This is an open access article distributed under the <a rel="license" href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution License</a>, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.':
                {'type': 'cc-by', # license type, see the licenses module for available ones
                 'version':'3.0', # version of the license if specified, can be blank

                    # also declare some properties which override info about this license in the licenses list (see licenses module)

                    'url': 'http://creativecommons.org/licenses/by/3.0'}
            }
        ]
        
        # some basic protection against missing fields in the incoming record
        """
        if "provider" not in record:
            return
        if "url" not in record["provider"]:
            return
        """
        # For all URL-s associated with this resource...
        #for url in record['provider']['url']:
        for url in record.provider_urls:
            # ... run the dumb string matcher if the URL is supported.
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)
