#!/bin/bash
set -e
exec celery -A app.task.celery_worker:celery_app worker --loglevel=info
