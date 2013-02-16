import requests
from copy import deepcopy
from datetime import datetime

from isitopenaccess.plugins import string_matcher

def page_license(record):
    """
    To respond to the provider identifier: http://www.biomedcentral.com
    
    This should determine the licence conditions of the BMC article and populate
    the record['bibjson']['license'] (note the US spelling) field.
    """

    # licensing statements to look for on this publisher's pages
    # take the form of {statement: meaning}
    # where meaning['id'] identifies the license (see licenses.py)
    # and meaning['version'] identifies the license version (if available)
    lic_statements = [
        {"This is an Open Access article distributed under the terms of the Creative Commons Attribution License (<a href='http://creativecommons.org/licenses/by/2.0'>http://creativecommons.org/licenses/by/2.0</a>), which permits unrestricted use, distribution, and reproduction in any medium, provided the original work is properly cited.":
            {'id': 'cc-by', 'version':'2.0', 'iioa': True}
        }
    ]

    string_matcher.simple_extract(lic_statements, record)
