from __future__ import absolute_import

from slavedriver.celery import celery
import config

@celery.task
def detect_provider(record):
    for fn in config.provider_detection.get(record["type"]):
        provider = fn(record)
        if provider is not None:
            record['provider'] = provider
            break
    return record
    
@celery.task    
def provider_site_plugins(record):
    fn = config.site_detection.get(record['provider'])
    licence = fn(record)
    if licence is not None:
        record["licence"] = licence
    return record
    
@celery.task
def provider_page_plugins(record):
    fn = config.page_detection.get(record['provider'])
    licence = fn(record)
    if licence is not None:
        record["licence"] = licence
    return record
