"""
This plugin handles Hindawi articles.
Hindawi publish from a single domain and use a consistent format for licenses
so this one should be relatively straightforward.
"""

# We import the plugin module from the isitopenaccess module, as this contains
# essential bits of infrastructure for us to build our plugin on.
from isitopenaccess import plugin

# Create a new class which extends the plugin.Plugin class.  The rest of this
# file shows how to extend and override the methods it provides signatures for
class HindawiPlugin(plugin.Plugin):
    _short_name = "hindawi"
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    # Specified without the schema (protocol - e.g. "http://") part.
    base_urls = ["www.hindawi.com"]
    # so if the http://www.hindawi.com/journals/ecam/2013/429706/ URL comes in,
    # it should be supported.
    
    # You can keep the supports() function as it is if your publisher only has
    # a few domain names and doesn't need anything more special than
    # "Does this URL start with this domain name?"
    def supports(self, provider):
        """
        Does this plugin support this provider
        """
        
        work_on = self.clean_urls(provider.get("url", []))

        for url in work_on:
            if self.supports_url(url):
                return True

        return False

    # This is what actually does the analysis on an incoming URL.
    # You can keep it as-is unless your publisher has many websites, in which case
    # you might want to match a regex like "^*.mypublisher.com" .
    def supports_url(self, url):
        """
        Same as the supports() function but answers the question for a single URL.
        """
        for bu in self.base_urls:
            if self.clean_url(url).startswith(bu):
                return True
        return False

    # The function that does the license extraction itself.
    # You should modify this:
    # 1. The docstring at the top, stating which provider (publisher) it supports.
    # 2. The licensing statements: how can the plugin know if a certain license
    # is in force? You need to define at least one such statement.
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
                 'open_access': True, # Is the license open access compliant? Up to you!
                 'BY': True, # Does it require attribution?
                 'NC': False, # Does it have non-commercial restrictions?
                 'SA': False, # Does it require distribution of derivative works under the same license?
                 'ND': False, # Does it forbid the creation of derivative works?

                    # also declare some properties which override info about this license in the licenses list (see licenses module)

                    # The list in the licenses module sometimes has more
                    # general information - for example, it doesn't link to a
                    # specific version of the CC-BY license, just the
                    # opendefinition.org page for it. This plugin knows a better
                    # URL though, since it's present in the license statement above.
                    'url': 'http://creativecommons.org/licenses/by/3.0'}
            }
        ]
        
        # some basic protection against missing fields in the incoming record
        if "provider" not in record:
            return
        if "url" not in record["provider"]:
            return
        
        # For all URL-s associated with this resource...
        for url in record['provider']['url']:
            # ... run the dumb string matcher if the URL is supported.
            if self.supports_url(url):
                self.simple_extract(lic_statements, record, url)
