#!/bin/sh
set -e

[ -f .env ] && export $(grep -v '^#' .env | xargs)

until nc -z "$DB_HOST" "$DB_PORT"; do sleep 2; done

alembic upgrade head
exec uvicorn main:app --host 0.0.0.0 --port 8000
