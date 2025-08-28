#!/bin/sh
set -eu
exec celery -A app.tasks.celery_worker worker -l info
