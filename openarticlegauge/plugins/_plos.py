from openarticlegauge import plugin

class PLOSPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    __desc__ = "Handles articles from PLOS"
    
    _base_urls = ["www.plosone.org", "www.plosbiology.org", "www.plosmedicine.org",
                 "www.ploscompbiol.org", "www.plosgenetics.org", "www.plospathogens.org",
                 "www.plosntds.org"]
    
    _license_mappings = [
            {"This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.":
                {'type': 'uk-ogl'}
            },
            {"This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.":
                {'type': 'cc-by'}
            },
            {"This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.":
                {'type': 'cc-by'}
            },
            {"This is an Open Access article in the spirit of the Public Library of Science (PLoS) principles for Open Access http://www.plos.org/oa/, without any waiver of WHO's privileges and immunities under international law, convention, or agreement. This article should not be reproduced for use in association with the promotion of commercial products, services, or any legal entity. There should be no suggestion that WHO endorses any specific organization or products. The use of the WHO logo is not permitted. This notice should be preserved along with the article's original URL.":
                {'type': 'plos-who'}
            },
            {"This is an open-access article, free of all copyright, and may be freely reproduced, distributed, transmitted, modified, built upon, or otherwise used by anyone for any lawful purpose. The work is made available under the Creative Commons CC0 public domain dedication.":
                {'type': 'cc-zero'}
            },
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
        return self.supports_by_base_url(provider)
        
    def license_detect(self, record):
        """
        To respond to the PLoS provider indentifiers (see config.license_detection)
        
        This should determine the licence conditions of the PLoS article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # licensing statements to look for on this publisher's pages
        # take the form of {statement: meaning}
        # where meaning['type'] identifies the license (see licenses.py)
        # and meaning['version'] identifies the license version (if available)
        lic_statements = self._license_mappings
        
        for url in record.provider_urls:
            if self.supports_base_url(url):
                self.simple_extract(lic_statements, record, url)

        return (self._short_name, self.__version__)

