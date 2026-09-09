#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

pause_on_error() {
  echo ""
  echo "Demo could not start. Read the error above."
  read -r -p "Press Enter to close..."
}
trap pause_on_error ERR

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed."
  echo "Download it from: https://www.python.org/downloads/"
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "First-time setup: creating the demo environment..."
  python3 -m venv .venv
fi

if [ ! -f ".venv/.demo_requirements_ready" ]; then
  echo "First-time setup: installing required packages..."
  .venv/bin/python -m pip install -r requirements.txt
  touch .venv/.demo_requirements_ready
fi

FRESH_DATABASE=0
if [ ! -f "db.sqlite3" ]; then
  FRESH_DATABASE=1
fi

echo "Preparing the local demo database..."
USE_SQLITE=1 DEBUG=1 .venv/bin/python manage.py migrate --noinput
if [ "$FRESH_DATABASE" -eq 1 ]; then
  echo "Adding sample products..."
  USE_SQLITE=1 DEBUG=1 .venv/bin/python seed_products.py
fi
USE_SQLITE=1 DEBUG=1 .venv/bin/python manage.py create_staff --reset
ADMIN_PASSWORD="AdminMatcha2026!" USE_SQLITE=1 DEBUG=1 \
  .venv/bin/python manage.py create_admin --reset

echo ""
echo "======================================================"
echo " MATCHA SHOP DEMO IS STARTING"
echo " Store: http://127.0.0.1:8000/"
echo " Staff: staff / StaffMatcha2026!"
echo " Admin: admin / AdminMatcha2026!"
echo " Stop:  press Control + C"
echo "======================================================"
echo ""

(sleep 2; open "http://127.0.0.1:8000/") &
USE_SQLITE=1 DEBUG=1 exec .venv/bin/python manage.py runserver 127.0.0.1:8000
