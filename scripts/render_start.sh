#!/usr/bin/env bash
# Render start script — run from repo root (set as Start Command).
set -euo pipefail

cd backend
export PYTHONPATH=.

echo "==> migrate"
python manage.py migrate --noinput

echo "==> seed_demo"
python manage.py seed_demo

echo "==> gunicorn"
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
