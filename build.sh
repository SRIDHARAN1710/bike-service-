#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r bike_service_backend/requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate
