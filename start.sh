#!/bin/sh
set -e

echo "Waiting for MySQL..."

for i in $(seq 15); do
  nc -z mysql 3306 && break
  sleep 1
done

nc -z mysql 3306 || { echo "MySQL not available after waiting"; exit 1; }

[ ! -d migrations ] && flask db init
flask db migrate -m "auto migration" || true
flask db upgrade

exec gunicorn -b 0.0.0.0:5000 run:app
