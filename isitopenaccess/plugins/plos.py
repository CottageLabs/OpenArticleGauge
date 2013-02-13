import requests
from copy import deepcopy
from datetime import datetime

from isitopenaccess import config
from isitopenaccess.licenses import LICENSES
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

def page_license(record):
    """
    To respond to the PLoS provider indentifiers (see config.license_detection)
    
    This should determine the licence conditions of the PLoS article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """

    # licensing statements to look for on this publisher's pages
    # take the form of {statement: meaning}
    # where meaning['id'] identifies the license (see licenses.py)
    # and meaning['version'] identifies the license version (if available)
    lic_statements = [
        {"This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.":
            {'id': 'uk-ogl', 'iioa': True}
        },
        {"This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.":
            {'id': 'cc-by', 'iioa': True}
        },
        {"This is an Open Access article in the spirit of the Public Library of Science (PLoS) principles for Open Access http://www.plos.org/oa/, without any waiver of WHO's privileges and immunities under international law, convention, or agreement. This article should not be reproduced for use in association with the promotion of commercial products, services, or any legal entity. There should be no suggestion that WHO endorses any specific organization or products. The use of the WHO logo is not permitted. This notice should be preserved along with the article's original URL.":
            {'id': 'cc-by', 'iioa': True}
        }
    ]
    # get content
    r = requests.get(record['provider'])
    
    # see if one of the licensing statements is in content 
    # and populate record with appropriate license info
    for statement_mapping in lic_statements:
        # get the statement string itself - always the first key of the dict
        # mapping statements to licensing info
        statement = statement_mapping.keys()[0]

        if statement in r.content:
            # okay, statement found on the page -> get license id (, version)
            lic_id = statement_mapping[statement]['id']
            lic_version = statement_mapping[statement].get('version', '')

            # license identified, now use that to construct the license object
            license = deepcopy(LICENSES[lic_id])
            license['version'] = lic_version
            license['description'] = ''

            # add provenance information to the license object
            provenance = {
                'date': datetime.now().isoformat(),
                'iioa': statement_mapping[statement]['iioa'],
                'source': record['provider'],
                'agent': config.agent,
                'jurisdiction': '', # TODO later (or later version of IIOA!)
                'category': 'page_scrape', # TODO we need to think how the
                    # users get to know what the values here mean.. docs?
                'description': cpl.gen_provenance_description(record['provider'], statement)
            }

            license['provenance'] = provenance

            record['bibjson']['license'] = license
