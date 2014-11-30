#!/bin/bash
# start a celery beat instance which will publish flush_buffer requests
# to the flush_buffer queue
celery beat --app=openarticlegauge.slavedriver --pidfile=beat.pid --logfile=beat.log -l info --detach
