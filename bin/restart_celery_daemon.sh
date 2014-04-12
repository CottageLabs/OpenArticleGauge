#!/bin/bash
celery multi restart 11 -A openarticlegauge.slavedriver -l info --pidfile=%n.pid --logfile=%n.log -Q:1-3 detect_provider -Q:4-6 provider_licence -Q:7 store_results -Q:8 flush_buffer -Q:9 priority_detect_provider -Q:10 priority_provider_licence -Q:11 priority_store_results
