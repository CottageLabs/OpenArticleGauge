from openarticlegauge import config
from datetime import datetime

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
    
