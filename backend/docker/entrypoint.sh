#!/bin/bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
exec gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
