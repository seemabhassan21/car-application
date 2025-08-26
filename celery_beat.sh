#!/bin/bash
set -e
exec celery -A app.tasks.celery_worker.celery beat --loglevel=info
