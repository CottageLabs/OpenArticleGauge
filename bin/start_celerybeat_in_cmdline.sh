#!/bin/bash

# Run celery beat in a commandline window to monitor it
celery worker --app=openarticlegauge.slavedriver -B -l info
