from datetime import datetime

from isitopenaccess import config

# TODO make these generate whole provenance objects, not just the description
# The contents of "date", "agent" and so on is the same across all plugins...
def gen_provenance_description(source_url, statement):
    return 'License decided by scraping the resource at ' + source_url + ' and looking for the following license statement: "' + statement + '".'

def gen_provenance_description_fail(source_url):
    return 'We have found it impossible or prohibitively difficult to decide what the license of this item is by scraping the resource at ' + source_url + '. See "error_message" in the "license" object for more information.'

def describe_license_fail(record, why, suggested_solution=''):
    record['bibjson'].setdefault('license', [])

    license = {
        "description": "",
        "title": "",
        "url": "",
        "version": "",
        "jurisdiction": "",
        "type": "failed-to-obtain-license",
        "open_access": False,
        "BY": "",
        "NC": "",
        "ND": "",
        "SA": "",
        "error_message": why,
        "suggested_solution": suggested_solution,
        "provenance": {
            "category": "page_scrape",
            "description": gen_provenance_description_fail(record.get('provider', {}).get('url', "none")),
            "agent": config.agent,
            "source": record.get('provider', {}).get('url', "unknown"),
            "date": datetime.strftime(datetime.now(), config.date_format)
        }
     }


    record['bibjson']['license'].append(license)
