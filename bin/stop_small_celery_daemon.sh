#!/bin/bash

# Stop the 11 celery workers
celery multi stop 8 -A openarticlegauge.slavedriver -l info --concurrency=4 --pidfile=%n.pid --logfile=%n.log -Q:1 detect_provider -Q:2-5 provider_licence -Q:6 store_results -Q:7 flush_buffer -Q:8 priority_detect_provider,priority_provider_licence,priority_store_results

# send a kill request for the pid in the beat.pid file.  This means, of course, that you need to run this script in the right directory
kill -TERM `cat beat.pid`
