from __future__ import absolute_import

from slavedriver.celery import celery

# Tasks should use a chaining strategy. Think of it as being a receipt
# that is passed from task to task, containing all the key results 
# and data that preceded it.

# eg {'lookup': {dict of info describing the lookup}},
#     'results': [list of plugin responses, in attempt order],}

# Task would then be passed this structure, add its reponse to the 'results'
# list and return the whole data structure. This also makes it easy to limit
# things like program-requested retries (as opposed to broker/celery retries).

@celery.task
def plos_lookup(job):
    return "%s - DOI?" % job
