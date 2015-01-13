from openarticlegauge import plugin
from openarticlegauge.models import Publisher
from openarticlegauge.util import http_stream_get

class EPMCLicensePlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

    # The domains that this plugin will say it can support.
    _base_urls = ["europepmc.org"]

    __desc__ = \
"""Obtains licenses from articles present in EuropePMC

It will use all license statements from registered publishers who have these URLs: {urls}

So ideally EuropePMC will be registered as a publisher. If it fails to find it, the plugin will fall back to some hardcoded license statements.
""".format(urls=", ".join(_base_urls))
    
    _license_mappings = [
        {'This is an open-access article distributed under the terms of the Creative Commons Attribution Non-commercial License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.':
            {
                'type': 'cc-by-nc', # license type, see the licenses module for available ones
            }
        }
    ]

    _author_manuscript_mappings = [
        {'Author Manuscript; Accepted for publication in peer reviewed journal':
            {
                "accepted_author_manuscript": True
            }
        },
        {'Author manuscript; available in PMC':
            {
                "accepted_author_manuscript": True
            }
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
        Does this plugin support this provider
        """
        return self.supports_by_base_url(provider)

    def license_detect(self, record):

        relevant_publishers = []
        for bu in self._base_urls:
            cburl = self.clean_url(bu)
            relevant_publishers += Publisher.find_by_journal_url('http://' + cburl)

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
                # TODO refactor self.simple_extract into several pieces
                # a downloader, a matcher, and a f() that records the license info
                # so the first two (and perhaps a general version of the third)
                # can be used here instead of this plugin having to do
                # all the work itself.
                r, content, content_length = http_stream_get(url)

                extra_provenance = {
                    "accepted_author_manuscript": False
                }

                for amm in self._author_manuscript_mappings:
                    statement = amm.keys()[0].strip()
                    if statement in content:
                        extra_provenance = amm[statement]
                        break

                print lic_statements
                self.simple_extract(lic_statements, record, url, content=content,
                                    extra_provenance=extra_provenance)


        return self._short_name, self.__version__