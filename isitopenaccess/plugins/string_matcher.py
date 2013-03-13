# DEPRECATED, AFTER PLUGIN REFACTOR WILL BE REMOVED

'''
import requests
from copy import deepcopy
from datetime import datetime

from isitopenaccess import config
from isitopenaccess.licenses import LICENSES
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

def simple_extract(handler, handler_version, lic_statements, record, url):
    """
    Generic code which looks for a particular string in a given web page (URL),
    determines the licence conditions of the article and populates
    the record['bibjson']['license'] (note the US spelling) field.

    The URL it analyses, the statements it looks for and the resulting licenses
    are passed in. This is not a plugin for a particular publisher - it just
    contains (allows re-use) the logic that any "dumb string matching" plugin 
    would use.

    :param handler: The name of the plugin which called this function to
    handle the record.
    :param handler_version: The __version__ of the plugin which called this
    function to handle the record.
    :param lic_statements: licensing statements to look for on this publisher's 
    pages. Take the form of {statement: meaning}
    where meaning['type'] identifies the license (see licenses.py)
    and meaning['version'] identifies the license version (if available)
    See a publisher plugin for an example, e.g. bmc.py
    :param record: a request for the IIOA status of an article, see IIOA docs for
    more info.
    :param url: source url of the item to be fetched. This is where the HTML
    page that's going to be scraped is expected to reside.
    """

    # get content
    r = requests.get(url)
    
    # see if one of the licensing statements is in content 
    # and populate record with appropriate license info
    for statement_mapping in lic_statements:
        # get the statement string itself - always the first key of the dict
        # mapping statements to licensing info
        statement = statement_mapping.keys()[0]

        if statement in r.content:
            # okay, statement found on the page -> get license type
            lic_type = statement_mapping[statement]['type']

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
            license.update(statement_mapping[statement])
            
            # add provenance information to the license object
            provenance = {
                'date': datetime.strftime(datetime.now(), config.date_format),
                'source': url,
                'agent': config.agent,
                'category': 'page_scrape', # TODO we need to think how the
                    # users get to know what the values here mean.. docs?
                'description': cpl.gen_provenance_description(url, statement),
                'handler': handler, # the name of the plugin processing this record
                'handler_version': handler_version # version of the plugin processing this record
            }

            license['provenance'] = provenance

            record['bibjson'].setdefault('license', [])
            record['bibjson']['license'].append(license)
'''
