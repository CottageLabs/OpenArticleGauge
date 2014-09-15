#!/bin/bash

celery multi start 8 -A openarticlegauge.slavedriver -l info --concurrency=4 --pidfile=%n.pid --logfile=%n.log -Q:1 detect_provider -Q:2-5 provider_licence -Q:6 store_results -Q:7 flush_buffer -Q:8 priority_detect_provider,priority_provider_licence,priority_store_results

# start a celery beat instance which will publish flush_buffer requests
# to the flush_buffer queue (managed by Worker 8 above)
celery beat --app=openarticlegauge.slavedriver --pidfile=beat.pid --logfile=beat.log -l info --detach

