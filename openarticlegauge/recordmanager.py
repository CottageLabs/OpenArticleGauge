"""
Some utility functions which can operate over the OAG record object, to help
plugins and other parts of the application ensure that when they add/modify
it, they do so in the correct way.

Basically this is the stem of a future class based around the record, rather
than passing around a python data structure - but making it so is a task for the
future (if at all - the python data structure has some utility that a class might not)

"""

from openarticlegauge import config
from datetime import datetime

def record_provider_url(record, url):
    """
    Record a provider url in the record
    
    This is equivalent to placing the supplied url in record['provider']['url'] which is a list of urls
    
    arguments:
    record -- OAG record object; see top-level documentation for details on its structure
    url -- the url to be added to the provider record
    
    """
    if not "provider" in record:
        record['provider'] = {}
    if not "url" in record["provider"]:
        record["provider"]["url"] = []
    if url not in record['provider']['url']:
        record['provider']['url'].append(url)
    
def record_provider_urls(record, urls):
    """
    Record a list of provider urls in the record
    
    This is just a wrapper for repeated calls to record_provider_url, so look there for the documentation
    
    arguments:
    record -- OAG record object; see top-level documentation for details on its structure
    urls -- the urls to be added to the provider record
    
    """
    for url in urls:
        record_provider_url(record, url)

def record_provider_doi(record, doi):
    """
    Record a DOI in the provider part of the record
    
    This is equivalent to placing the supplied doi in record['provider']['doi'] which is a single value field
    
    arguments:
    record -- OAG record object; see top-level documentation for details on its structure
    doi -- the doi to be added to the provider record
    """
    if not "provider" in record:
        record['provider'] = {}
    record["provider"]["doi"] = doi
    
def add_license(record,
                description="",
                title="",
                url="",
                version="",
                jurisdiction="",
                type="",
                open_access=False,
                BY="",
                NC="",
                ND="",
                SA="",
                error_message="",
                suggested_solution="",
                category="",
                provenance_description="",
                agent=config.agent,
                source="",
                date=datetime.strftime(datetime.now(), config.date_format),
                handler="",
                handler_version=""):
    """
    Add a licence with the supplied keyword parameters to the record in the appropriate format.
    
    The format of the licence is as follows:
    {
        "description": "",
        "title": "",
        "url": licence_url,
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
            "description": self.gen_provenance_description_fail(source_url),
            "agent": config.agent,
            "source": source_url,
            "date": datetime.strftime(datetime.now(), config.date_format),
            "handler" : self._short_name,
            "handler_version" : self.__version__
        }
    }
    
    keyword_arguments:
    see the top level documentation for details on the meaning of each field - they map consistently to the parts
    of the licence record
    
    """
    
    if "bibjson" not in record:
        record["bibjson"] = {}
    if "license" not in record['bibjson']:
        record['bibjson']['license'] = []
    
    record['bibjson']['license'].append(
        {
            "description": description,
            "title": title,
            "url": url,
            "version": version,
            "jurisdiction": jurisdiction,
            "type": type,
            "open_access": open_access,
            "BY": BY,
            "NC": NC,
            "ND": ND,
            "SA": SA,
            "error_message": error_message,
            "suggested_solution": suggested_solution,
            "provenance": {
                "category": category,
                "description": provenance_description,
                "agent": agent,
                "source": source,
                "date": date,
                "handler" : handler,
                "handler_version" : handler_version
            }
        }
    )
    
