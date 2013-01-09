from __future__ import absolute_import

from slavedriver.celery import celery

@celery.task
def plos_lookup(doi):
    return "%s - DOI?" % doi
