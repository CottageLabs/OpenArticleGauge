#!/bin/bash

# Stop the 11 celery workers
celery multi stop 11 -A openarticlegauge.slavedriver -l info --pidfile=%n.pid --logfile=%n.log -Q:1-3 detect_provider -Q:4-6 provider_licence -Q:7 store_results -Q:8 flush_buffer -Q:9 priority_detect_provider -Q:10 priority_provider_licence -Q:11 priority_store_results

# send a kill request for the pid in the beat.pid file.  This means, of course, that you need to run this script in the right directory
kill -TERM `cat beat.pid`
