# IMPORTANT! This user should exist if you use this in deployment!
# Workers should run as an unprivileged user.
# CELERYD_USER = 'celery'
# CELERYD_GROUP = 'celery'
import os

# CELERYD_NODES = 'w1'

# Where to chdir at start.
# CELERYD_CHDIR = '/path/to/isitopenaccess/'

# Python interpreter from environment.
# ENV_PYTHON="$CELERYD_CHDIR/env/bin/python"

# Extra arguments to celeryd
CELERYD_OPTS = '--time-limit=300 --concurrency=8'

# Name of the celery config module.
CELERY_CONFIG_MODULE = 'isitopenaccess.celeryconfig'

# %n will be replaced with the nodename.
#CELERYD_LOG_FILE = 'celery/log/%n.log')
#CELERYD_PID_FILE = 'celery/run/%n.pid'

BROKER_URL = 'redis://localhost'
CELERY_RESULT_BACKEND = "redis://localhost"
CELERY_IMPORTS = ('isitopenaccess.workflow',)

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_ROUTES = {
    'isitopenaccess.workflow.detect_provider' : {"queue": "detect_provider"},
    'isitopenaccess.workflow.provider_licence' : {"queue" : "provider_licence"},
    'isitopenaccess.workflow.store_results' : {"queue" : "store_results"}
}
