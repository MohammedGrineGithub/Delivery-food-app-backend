#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Apply database migrations
echo "==================== Applying database migrations... ===================="
python3 manage.py makemigrations
python3 manage.py migrate

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 1 --reload --reload-engine=poll app.wsgi:application