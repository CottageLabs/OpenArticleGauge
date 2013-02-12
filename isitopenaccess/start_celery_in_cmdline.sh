#!/bin/bash

# Run celery in a commandline window to monitor it
# Running in 'screen' might be an idea...
celery worker --app=slavedriver -l info

# (Of course there is the daemonised way to run it.)
