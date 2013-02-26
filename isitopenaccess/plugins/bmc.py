from isitopenaccess.plugins import string_matcher

def supports(provider):
    """
    Does the page_license plugin support this provider
    """
    base_urls = ["www.biomedcentral.com"]
    
    for url in provider.get("url", []):
        # strip any leading http:// or https://
        if url.startswith("http://"):
            url = url[len("http://"):]
        elif url.startswith("https://"):
            url = url[len("https://"):]
        
        for bu in base_urls:
            if url.startswith(bu):
                return True
                
    return False

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

    string_matcher.simple_extract(lic_statements, record)
