# IMPORTANT! This user should exist if you use this in deployment!
# Workers should run as an unprivileged user.
# CELERYD_USER = 'celery'
# CELERYD_GROUP = 'celery'

CELERYD_NODES = 'w1'

# Where to chdir at start.
# CELERYD_CHDIR = '/path/to/isitopenaccess/'

# Python interpreter from environment.
# ENV_PYTHON="$CELERYD_CHDIR/env/bin/python"

# Extra arguments to celeryd
CELERYD_OPTS = '--time-limit=300 --concurrency=8'

# Name of the celery config module.
CELERY_CONFIG_MODULE = 'celeryconfig'

# %n will be replaced with the nodename.
CELERYD_LOG_FILE = '/var/log/celery/%n.log'
CELERYD_PID_FILE = '/var/run/celery/%n.pid'

BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_IMPORTS = ('slavedriver.webfetch',)

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
