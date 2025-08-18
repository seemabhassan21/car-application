#!/bin/sh
celery -A app.tasks.celery_worker.celery worker --loglevel=info
