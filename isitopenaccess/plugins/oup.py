from isitopenaccess.plugins import string_matcher
import re

def supports(provider):
    """
    Does the page_license plugin support this provider
    """
    rx = '(http|https){0,1}://.+?\.oxfordjournals.org/.+'
    
    for url in provider.get("url", []):
        if re.match(rx, url):
            return True
                
    return False

def page_license(record):
    """
    To respond to the provider identifier: *.oxfordjournals.org
    
    This should determine the licence conditions of the OUP article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """

    # licensing statements to look for on this publisher's pages
    # take the form of {statement: meaning}
    # where meaning['type'] identifies the license (see licenses.py)
    # and meaning['version'] identifies the license version (if available)
    lic_statements = [
        {"""This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),
                     which permits unrestricted reuse, distribution, and reproduction in any medium, provided the original work is properly cited.""":
            {'type': 'cc-by', 'version':'3.0', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False,
                # also declare some properties which override info about this license in the licenses list (see licenses module)
                'url': 'http://creativecommons.org/licenses/by/3.0/'}
        },
        { # this license statement is the same as the one above, but somebody's missed out the "reuse" word after unrestricted
        """This is an Open Access article distributed under the terms of the Creative Commons Attribution License (http://creativecommons.org/licenses/by/3.0/),
                     which permits unrestricted, distribution, and reproduction in any medium, provided the original work is properly cited.""":
            {'type': 'cc-by', 'version':'3.0', 'open_access': True, 'BY': True, 'NC': False, 'SA': False, 'ND': False,
                # also declare some properties which override info about this license in the licenses list (see licenses module)
                'url': 'http://creativecommons.org/licenses/by/3.0/'}
        },
        {"""This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License (http://creativecommons.org/licenses/by-nc/3.0),
                     which permits unrestricted non-commercial use, distribution, and reproduction in any medium, provided the original work is
                     properly cited.""":
            {'type': 'cc-nc', 'version':'3.0', 'open_access': True, 'BY': True, 'NC': True, 'SA': False, 'ND': False,
                # also declare some properties which override info about this license in the licenses list (see licenses module)
                'url': 'http://creativecommons.org/licenses/by-nc/3.0'}
        }
    ]

    string_matcher.simple_extract(lic_statements, record)
