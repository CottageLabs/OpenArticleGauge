"""
Initialise the Celery instance to be used by the application

This is largely just boiler plate, and we could probably look at coming back to it and cleaning it
up a bit in the future.

"""
from __future__ import absolute_import

from celery import Celery

celery = Celery()

from openarticlegauge import celeryconfig

celery.config_from_object(celeryconfig)

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    celery.start()
