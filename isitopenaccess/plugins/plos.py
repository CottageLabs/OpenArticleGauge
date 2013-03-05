from isitopenaccess.plugins import string_matcher
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

base_urls = ["www.plosone.org", "www.plosbiology.org", "www.plosmedicine.org",
                 "www.ploscompbiol.org", "www.plosgenetics.org", "www.plospathogens.org",
                 "www.plosntds.org"]

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
    To respond to the PLoS provider indentifiers (see config.license_detection)
    
    This should determine the licence conditions of the PLoS article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """

    # licensing statements to look for on this publisher's pages
    # take the form of {statement: meaning}
    # where meaning['type'] identifies the license (see licenses.py)
    # and meaning['version'] identifies the license version (if available)
    lic_statements = [
        {"This is an open-access article distributed under the terms of the free Open Government License, which permits unrestricted use, distribution and reproduction in any medium, provided the original author and source are credited.":
            {'type': 'uk-ogl', 'version':'', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False}
        },
        {"This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any medium, provided the original author and source are credited.":
            {'type': 'cc-by', 'version':'', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False}
        },
        {"This is an Open Access article in the spirit of the Public Library of Science (PLoS) principles for Open Access http://www.plos.org/oa/, without any waiver of WHO's privileges and immunities under international law, convention, or agreement. This article should not be reproduced for use in association with the promotion of commercial products, services, or any legal entity. There should be no suggestion that WHO endorses any specific organization or products. The use of the WHO logo is not permitted. This notice should be preserved along with the article's original URL.":
            {'type': 'plos-who', 'version':'', 'open_access': True, 'BY': True, 'NC': '', 'SA': False, 'ND': False}
        }
    ]

    for url in record['provider']['url']:
        if supports_url(url):
            string_matcher.simple_extract(lic_statements, record, url)
