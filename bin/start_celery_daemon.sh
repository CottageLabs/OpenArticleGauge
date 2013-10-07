#!/bin/bash

# start 8 celery workers for processing the various functions.
# Workers 1, 2 and 3 will work together to manage the detect_provider queue
# Workers 3, 4, 5 and 6 will work together to manage the provider_licence queue
# Worker 7 will be responsible for processing the store_results queue
# Worker 8 will be responsible for processing the flush_buffer queue
celery multi start 8 -A openarticlegauge.slavedriver -l info --pidfile=%n.pid --logfile=%n.log -Q:1-3 detect_provider -Q:4-6 provider_licence -Q:7 store_results -Q:8 flush_buffer

# start a celery beat instance which will publish flush_buffer requests
# to the flush_buffer queue (managed by Worker 8 above)
celery beat --app=openarticlegauge.slavedriver --pidfile=beat.pid --logfile=beat.log -l info --detach

