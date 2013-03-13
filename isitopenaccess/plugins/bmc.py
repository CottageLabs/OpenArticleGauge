_short_name = __name__.split(".")[-1]
__version__='0.1' # consider incrementing or at least adding a minor version
                    # e.g. "0.1.1" if you change this plugin

from isitopenaccess.plugins import string_matcher
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

base_urls = ["www.biomedcentral.com"]

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
    To respond to the provider identifier: http://www.biomedcentral.com
    
    This should determine the licence conditions of the BMC article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """

    # licensing statements to look for on this publisher's pages
    # take the form of {statement: meaning}
    # where meaning['type'] identifies the license (see licenses.py)
    # and meaning['version'] identifies the license version (if available)
    lic_statements = [
        {"This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.":
            {'type': 'cc-by', 'version':'2.0', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False,
                # also declare some properties which override info about this license in the licenses list (see licenses module)
                'url': 'http://creativecommons.org/licenses/by/2.0'}
        }
    ]

    for url in record['provider']['url']:
        if supports_url(url):
            string_matcher.simple_extract(_short_name, __version__, lic_statements, record, url)
