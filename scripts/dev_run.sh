#!/usr/bin/env bash
# Local dev: migrate + runserver (SQLite fallback when Postgres is down)
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    docker compose up -d db 2>/dev/null || true
    echo "Waiting for PostgreSQL…"
    for _ in $(seq 1 30); do
      if docker compose exec -T db pg_isready -U matcha -d matcha_shop >/dev/null 2>&1; then
        echo "PostgreSQL ready."
        break
      fi
      sleep 1
    done
  else
    echo "Docker installed but daemon not running — will use SQLite if Postgres unreachable."
  fi
fi

python manage.py migrate --noinput
echo ""
echo "→ Store:  http://127.0.0.1:8000/"
echo "→ Login:  http://127.0.0.1:8000/login/"
echo "→ Admin:  http://127.0.0.1:8000/admin/  (superuser only)"
echo "→ Staff:  http://127.0.0.1:8000/staff/"
echo ""
exec python manage.py runserver
