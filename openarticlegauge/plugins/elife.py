from openarticlegauge import plugin, config
from openarticlegauge.licenses import LICENSES
from openarticlegauge import oa_policy
import requests, logging
from lxml import etree
from copy import deepcopy
from datetime import datetime

log = logging.getLogger(__name__)

class ELifePlugin(plugin.Plugin):
    _short_name = __name__.split('.')[-1]
    __version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin
    __desc__ = "Extracts licence information from the eLife API"
    
    _base_urls = ["elife.elifesciences.org"]
    
    _license_mappings = [
            {'//license[@xlink:href="http://creativecommons.org/licenses/by/3.0/" and @license-type="open-access"]': 
                {
                    'type': 'cc-by', 'version':'3.0',
                    # also declare some properties which override info about this license in the licenses list (see licenses module)
                    'url': 'http://creativecommons.org/licenses/by/3.0/'
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
        Does the license_detect plugin support this provider
        """
        return self.supports_by_base_url(provider)
    
    def license_detect(self, record):
        """
        To respond to the provider identifier: http://elife.elifesciences.org
        
        This should determine the licence conditions of the eLife article and populate
        the record['bibjson']['license'] (note the US spelling) field.
        """

        # List of licensing statements to look for on this publisher's pages.
        # In eLife's case they take the form of {xpath string: meaning object}
        # since we're not scraping HTML, we're using an XML API.
        # meaning['type'] identifies the license (see licenses.py)
        # and meaning['version'] identifies the license version (if available)
        elife_license_mappings = self._license_mappings

        # 1. get DOI from record object
        # doi = record['provider'].get('doi')
        doi = record.doi_without_prefix  # it MUST NOT HAVE the canonical DOI prefix, "doi:" or "DOI:"

        if doi:
        # 2. query elife XML api
            url = 'http://elife.elifesciences.org/elife-source-xml/' + doi
            response = requests.get(url)
            
            # determine the size of the request
            # (we ignore the content-length header, and just always use the number of bytes that we
            # calculate ourselves)
            source_size = len(bytes(response.content))

            try:
                xml = etree.fromstring(response.text.decode("utf-8", "ignore"))
            except Exception as e:
                log.error("Error parsing the XML from " + url)
                log.error(e)
                return None  # no point in doing anything else, so just do what
                             # Python would do anyway upon reaching the end of this function
        
            # process the XML response
            namespaces = {'xlink': 'http://www.w3.org/1999/xlink'}

            for mapping in elife_license_mappings:
                xpath = mapping.keys()[0]
                meaning = mapping[xpath]
                elements = xml.xpath(xpath, namespaces=namespaces)

                if len(elements) > 0:
                    lic_type = meaning['type']
        
                    # license identified, now use that to construct the license object
                    license = deepcopy(LICENSES[lic_type])
                    license['open_access'] = oa_policy.oa_for_license(lic_type)
                    # set some defaults which have to be there, even if empty
                    license.setdefault('version','')
                    license.setdefault('description','')
                    license.setdefault('jurisdiction','') # TODO later (or later version of OAG!)
        
                    # Copy over all information about the license from the license
                    # statement mapping. In essence, transfer the knowledge of the 
                    # publisher plugin authors to the license object.
                    # Consequence: Values coming from the publisher plugin overwrite
                    # values specified in the licenses module.
                    license.update(meaning)
        
                    # add provenance information to the license object
                    provenance = {
                        'handler': self._short_name,
                        'handler_version': self.__version__,
                        'date': datetime.strftime(datetime.now(), config.date_format),
                        'source': url,
                        "source_size" : source_size,
                        'agent': config.agent,
                        'category': 'xml_api', # TODO we need to think how the
                            # users get to know what the values here mean.. docs?
                        'description': 'License decided by querying the eLife XML API at ' + url
                    }
        
                    license['provenance'] = provenance
                    record.add_license_object(license)

        return (self._short_name, self.__version__)