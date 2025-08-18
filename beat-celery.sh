#!/bin/sh
celery -A app.tasks.celery_worker.celery beat --loglevel=info --schedule=/tmp/celerybeat-schedule
