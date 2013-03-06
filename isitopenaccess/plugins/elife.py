from isitopenaccess.plugins import string_matcher
from isitopenaccess.plugins import common as cpl # Common Plugin Logic

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

    # 1. get DOI from record object
    # record['identifier'] I think

    # 2. query elife XML api

    # 3. ???

    # 4. Profit!

    # 5. don't forget to add test_elife.py

    #for url in record['provider']['url']:
    #    if supports_url(url):
    #        string_matcher.simple_extract(lic_statements, record, url)
