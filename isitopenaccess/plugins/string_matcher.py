import requests
from copy import deepcopy
from datetime import datetime

from isitopenaccess import config
from isitopenaccess.licenses import LICENSES
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

def simple_extract(lic_statements, record):
    """
    Generic code which looks for a particular string in a given web page (URL),
    determines the licence conditions of the article and populates
    the record['bibjson']['license'] (note the US spelling) field.

    The URL it analyses, the statements it looks for and the resulting licenses
    are passed in. This is not a plugin for a particular publisher - it just
    contains (allows re-use) the logic that any "dumb string matching" plugin 
    would use.

    :param lic_statements: licensing statements to look for on this publisher's 
    pages. Take the form of {statement: meaning}
    where meaning['type'] identifies the license (see licenses.py)
    and meaning['version'] identifies the license version (if available)
    See a publisher plugin for an example, e.g. bmc.py
    :param record: a request for the IIOA status of an article, see IIOA docs for
    more info.
    """

    # get content
    url = record['provider']['url']
    r = requests.get(url)
    
    # see if one of the licensing statements is in content 
    # and populate record with appropriate license info
    for statement_mapping in lic_statements:
        # get the statement string itself - always the first key of the dict
        # mapping statements to licensing info
        statement = statement_mapping.keys()[0]

        if statement in r.content:
            # okay, statement found on the page -> get license id (, version)
            lic_type = statement_mapping[statement]['type']
            lic_version = statement_mapping[statement].get('version', '')

            # license identified, now use that to construct the license object
            license = deepcopy(LICENSES[lic_type])
            license['version'] = lic_version
            license['description'] = ''
            license['jurisdiction'] = '' # TODO later (or later version of IIOA!)
            
            # Copy over all information about the license from the license statement mapping
            # In essence, transfer the knowledge of the publisher plugin authors to the
            # license object.
            for attribute in statement_mapping[statement].keys():
                license[attribute] = statement_mapping[statement][attribute]
            
            # add provenance information to the license object
            provenance = {
                'date': datetime.now().isoformat(),
                'source': url,
                'agent': config.agent,
                'category': 'page_scrape', # TODO we need to think how the
                    # users get to know what the values here mean.. docs?
                'description': cpl.gen_provenance_description(url, statement)
            }

            license['provenance'] = provenance

            record['bibjson']['license'] = license
