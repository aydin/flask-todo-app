#!/usr/bin/env bash
source venv/bin/activate
flask db init
flask db migrate
flask db upgrade
exec gunicorn -b :5000 --access-logfile - --error-logfile - todo:app