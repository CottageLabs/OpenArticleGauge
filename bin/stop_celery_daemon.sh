#!/bin/bash

# To use an System V style init script. see:
# http://docs.celeryproject.org/en/latest/tutorials/daemonizing.html#daemonizing

# Make sure you are in the correct enviroment to run this.
# Eg in a virtualenv and as a suitable user.

# Start celery with a single worker node, 'w1'
# celery multi start w1 -A isitopenaccess.slavedriver -l info --pidfile=%n.pid --logfile=%n.log

# Restarting:
# celery multi restart w1 -A isitopenaccess.slavedriver -l info

# Stopping:
celery multi stop w1 -A isitopenaccess.slavedriver -l info --pidfile=%n.pid --logfile=%n.log
