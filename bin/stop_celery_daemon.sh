#!/bin/bash

# Stop the 8 celery workers
celery multi stop 8 -A openarticlegauge.slavedriver -l info --pidfile=%n.pid --logfile=%n.log -Q:1-3 detect_provider -Q:4-6 provider_licence -Q:7 store_results -Q:8 flush_buffer

# send a kill request for the pid in the beat.pid file.  This means, of course, that you need to run this script in the right directory
kill -TERM `cat beat.pid`
