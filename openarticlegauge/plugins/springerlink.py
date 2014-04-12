from openarticlegauge import plugin
from openarticlegauge.models import Publisher

class SpringerLinkPlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    _base_urls = ["link.springer.com"]

    __desc__ = \
"""Obtains licenses from articles published by SpringerLink

It will use all license statements from registered publishers who have these URLs: {urls}

So ideally Springer will be registered as a publisher. If it fails to find it, the plugin will fall back to some hardcoded license statements.

In order to see the rights / license statement on SpringerLink following an article's DOI is not enough.
/fulltext.html has to be appended to the article's URL to get a rights statement.
""".format(urls=", ".join(_base_urls))
    
    _license_mappings = [
        {'This article is distributed under the terms of the Creative Commons Attribution License which permits any use, distribution, and reproduction in any medium, provided the original author(s) and the source are credited.':
            {
                'type': 'cc-by', # license type, see the licenses module for available ones
            }
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
        Does this plugin support this provider
        """
        return self.supports_by_base_url(provider)

    def license_detect(self, record):

        relevant_publishers = []
        for bu in self._base_urls:
            cburl = self.clean_url(bu)
            relevant_publishers += Publisher.find_by_journal_url(cburl)

        lic_statements = []
        for pub in relevant_publishers:
            for l in pub['licenses']:
                lic_statement = {}
                lic_statement[l['license_statement']] = {'type': l['license_type'], 'version': l.get('version', '')}
                lic_statements.append(lic_statement)

        if not lic_statements:
            lic_statements = self._license_mappings

        for url in record.provider_urls:
            if self.supports_base_url(url):
                if not url.endswith('/fulltext.html'):
                    url += '/fulltext.html'
                self.simple_extract(lic_statements, record, url)
