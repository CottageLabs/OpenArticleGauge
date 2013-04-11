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
