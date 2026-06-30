#!/usr/bin/env bash
set -euo pipefail

mkdir -p media/slips

# Do not block the web port if DB is slow or unreachable at boot.
if command -v timeout >/dev/null 2>&1; then
  timeout 90 python manage.py migrate --noinput || echo "WARN: migrate failed or timed out; starting web anyway"
else
  python manage.py migrate --noinput || echo "WARN: migrate failed; starting web anyway"
fi

exec gunicorn config.wsgi \
  --workers 1 \
  --bind "0.0.0.0:${PORT:?PORT not set}" \
  --timeout 120 \
  --keep-alive 65
