#!/bin/sh
set -e 
[ ! -d migrations ] && flask db init
flask db migrate -m "auto migration" || true
flask db upgrade

exec gunicorn -b 0.0.0.0:5000 run:app
