#!/bin/bash

# Run celery in a commandline window to monitor it
# Running in 'screen' might be an idea...
celery worker --app=openarticlegauge.slavedriver -l info -Q detect_provider,provider_licence,store_results,flush_buffer,priority_detect_provider,priority_provider_licence,priority_store_results

# can't run beat in the same virtualenv, needs celery 3.0.13 and we're
# up to 3.0.25. Make a 2nd virtualenv and run
# start_celerybeat_in_cmdline.sh in there. :(.
# celery worker --app=openarticlegauge.slavedriver -B -l info -Q detect_provider,provider_licence,store_results,flush_buffer,priority_detect_provider,priority_provider_licence,priority_store_results

# (Of course there is the daemonised way to run it.)
