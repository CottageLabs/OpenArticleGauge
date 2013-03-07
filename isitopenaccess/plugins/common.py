from datetime import datetime

from isitopenaccess import config

# TODO make these generate whole provenance objects, not just the description
# The contents of "date", "agent" and so on is the same across all plugins...
def gen_provenance_description(source_url, statement):
    return 'License decided by scraping the resource at ' + source_url + ' and looking for the following license statement: "' + statement + '".'

def gen_provenance_description_fail(source_url):
    return 'We have found it impossible or prohibitively difficult to decide what the license of this item is by scraping the resource at ' + source_url + '. See "error_message" in the "license" object for more information.'

def describe_license_fail(record, source_url, why, suggested_solution=''):
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
            "description": gen_provenance_description_fail(source_url),
            "agent": config.agent,
            "source": source_url,
            "date": datetime.strftime(datetime.now(), config.date_format)
        }
     }


    record['bibjson']['license'].append(license)

def record_provider_url(record, url):
    if not "provider" in record:
        record['provider'] = {}
    if not "url" in record["provider"]:
        record["provider"]["url"] = []
    if url not in record['provider']['url']:
        record['provider']['url'].append(url)
    
def record_provider_urls(record, urls):
    for url in urls:
        record_provider_url(record, url)

def record_provider_doi(record, doi):
    if not "provider" in record:
        record['provider'] = {}
    record["provider"]["doi"] = doi

def clean_url(url):
    # strip any leading http:// or https://
    if url.startswith("http://"):
        url = url[len("http://"):]
    elif url.startswith("https://"):
        url = url[len("https://"):]

    return url

def clean_urls(urls):
    cleaned_urls = []
    for url in urls:
        cleaned_urls.append(clean_url(url))

    return cleaned_urls
