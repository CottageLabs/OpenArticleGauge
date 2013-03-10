import requests, logging
from lxml import etree
from copy import deepcopy
from datetime import datetime

from isitopenaccess.plugins import string_matcher
from isitopenaccess.plugins import common as cpl # Common Plugin Logic
from isitopenaccess.licenses import LICENSES
from isitopenaccess import config

log = logging.getLogger(__name__)

base_urls = ["elife.elifesciences.org"]

def supports(provider):
    """
    Does the page_license plugin support this provider
    """
    
    work_on = cpl.clean_urls(provider.get("url", []))

    for url in work_on:
        if supports_url(url):
            return True

    return False

def supports_url(url):
    for bu in base_urls:
        if cpl.clean_url(url).startswith(bu):
            return True

def page_license(record):
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
    elife_license_mappings = [
        {'//license[@xlink:href="http://creativecommons.org/licenses/by/3.0/" and @license-type="open-access"]': 
            {
                'type': 'cc-by', 'version':'3.0', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False,
                # also declare some properties which override info about this license in the licenses list (see licenses module)
                'url': 'http://creativecommons.org/licenses/by/3.0/'
            }
        }
    ]

    # 1. get DOI from record object
    if record['identifier']['type'] == 'doi':
        doi = record['identifier']['id']

    # 2. query elife XML api
        url = 'http://elife.elifesciences.org/elife-source-xml/' + doi
        response = requests.get(url)

        try:
            xml = etree.fromstring(response.text.decode("utf-8"))
        except Exception as e:
            log.error("Error parsing the XML from " + url)
            log.error(e)
    
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
                # set some defaults which have to be there, even if empty
                license.setdefault('version','')
                license.setdefault('description','')
                license.setdefault('jurisdiction','') # TODO later (or later version of IIOA!)
    
                # Copy over all information about the license from the license
                # statement mapping. In essence, transfer the knowledge of the 
                # publisher plugin authors to the license object.
                # Consequence: Values coming from the publisher plugin overwrite
                # values specified in the licenses module.
                license.update(meaning)
    
                # add provenance information to the license object
                provenance = {
                    'date': datetime.strftime(datetime.now(), config.date_format),
                    'source': url,
                    'agent': config.agent,
                    'category': 'xml_api', # TODO we need to think how the
                        # users get to know what the values here mean.. docs?
                    'description': 'License decided by querying the eLife XML API at ' + url
                }
    
                license['provenance'] = provenance
    
                record['bibjson'].setdefault('license', [])
                record['bibjson']['license'].append(license)
