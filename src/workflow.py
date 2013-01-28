from celery import chain
from slavedriver.workers import detect_provider, provider_site_plugins, provider_page_plugins

def start_back_end(record):
    ch = chain(detect_provider.s(record), provider_site_plugins.s(), provider_page_plugins.s())
    r = ch.apply_async()
    return r
