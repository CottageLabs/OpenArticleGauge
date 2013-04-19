"""
Standard Celery configuration file, for use in initialising the Celery system for OAG

"""

# IMPORTANT! This user should exist if you use this in deployment!
# Workers should run as an unprivileged user.
# CELERYD_USER = 'celery'
# CELERYD_GROUP = 'celery'
import os, config
from datetime import timedelta

# CELERYD_NODES = 'w1'

# Where to chdir at start.
# CELERYD_CHDIR = '/path/to/openarticlegauge/'

# Python interpreter from environment.
# ENV_PYTHON="$CELERYD_CHDIR/env/bin/python"

# Extra arguments to celeryd
CELERYD_OPTS = '--time-limit=300 --concurrency=8'

# Name of the celery config module.
CELERY_CONFIG_MODULE = 'openarticlegauge.celeryconfig'

# %n will be replaced with the nodename.
#CELERYD_LOG_FILE = 'celery/log/%n.log')
#CELERYD_PID_FILE = 'celery/run/%n.pid'

BROKER_URL = 'redis://localhost'
CELERY_RESULT_BACKEND = "redis://localhost"
CELERY_IMPORTS = ('openarticlegauge.workflow', 'openarticlegauge.models')

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_ROUTES = {
    'openarticlegauge.workflow.detect_provider' : {"queue": "detect_provider"},
    'openarticlegauge.workflow.provider_licence' : {"queue" : "provider_licence"},
    'openarticlegauge.workflow.store_results' : {"queue" : "store_results"},
    'openarticlegauge.models.flush_buffer' : {'queue' : 'flush_buffer'}
}

CELERYBEAT_SCHEDULE = {
    'flush_archive_buffer': {
        'task': 'openarticlegauge.models.flush_buffer',
        'schedule': timedelta(seconds=config.BUFFER_FLUSH_PERIOD),
        'options' : {
            'queue' : 'flush_buffer'
        }
    }
}

CELERY_TIMEZONE = 'UTC'
