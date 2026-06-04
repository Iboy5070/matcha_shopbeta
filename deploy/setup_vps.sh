#!/usr/bin/env bash
# ============================================================
# Matcha Shop — VPS Setup Script (Ubuntu 22.04)
# ຮັນດ້ວຍ: bash setup_vps.sh YOUR_DOMAIN.COM
# ============================================================
set -euo pipefail
DOMAIN="${1:?Usage: $0 <domain>}"
APP_DIR="/home/deploy/matcha_shopbeta"
PY="$APP_DIR/.venv/bin/python"
GIT_REPO="${GIT_REPO:-}"   # override ຖ້າຕ້ອງການ

echo "==> [1/9] Update packages"
apt-get update -q && apt-get upgrade -yq

echo "==> [2/9] Install dependencies"
apt-get install -yq \
    python3.11 python3.11-venv python3.11-dev \
    postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git gettext

echo "==> [3/9] Create deploy user"
id deploy &>/dev/null || useradd -m -s /bin/bash deploy
usermod -aG www-data deploy

echo "==> [4/9] Setup PostgreSQL"
sudo -u postgres psql <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='matcha') THEN
    CREATE ROLE matcha LOGIN PASSWORD 'CHANGE_THIS_PASSWORD';
  END IF;
END \$\$;
CREATE DATABASE matcha_shop OWNER matcha;
SQL
echo "   DB: postgres://matcha:CHANGE_THIS_PASSWORD@localhost/matcha_shop"

echo "==> [5/9] Clone / update repo"
if [ -d "$APP_DIR/.git" ]; then
    sudo -u deploy git -C "$APP_DIR" pull
else
    [ -n "$GIT_REPO" ] || { echo "Set GIT_REPO env var"; exit 1; }
    sudo -u deploy git clone "$GIT_REPO" "$APP_DIR"
fi

echo "==> [6/9] Python venv + dependencies"
sudo -u deploy python3.11 -m venv "$APP_DIR/.venv"
sudo -u deploy "$APP_DIR/.venv/bin/pip" install -q --upgrade pip
sudo -u deploy "$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "==> [7/9] Django: migrate + collectstatic"
# .env ຕ້ອງມີຢູ່ $APP_DIR/.env ກ່ອນຮັນ script ນີ້
sudo -u deploy "$PY" "$APP_DIR/manage.py" migrate --noinput
sudo -u deploy "$PY" "$APP_DIR/manage.py" compilemessages
sudo -u deploy "$PY" "$APP_DIR/manage.py" collectstatic --noinput
sudo -u deploy "$PY" "$APP_DIR/manage.py" seed_demo

echo "==> [8/9] Gunicorn systemd service"
mkdir -p /var/log/gunicorn
chown deploy:www-data /var/log/gunicorn
sed "s|YOUR_DOMAIN.COM|$DOMAIN|g" "$APP_DIR/deploy/gunicorn.service" \
    > /etc/systemd/system/matcha-gunicorn.service
systemctl daemon-reload
systemctl enable --now matcha-gunicorn

echo "==> [9/9] Nginx + SSL"
sed "s|YOUR_DOMAIN.COM|$DOMAIN|g" "$APP_DIR/deploy/nginx.conf" \
    > "/etc/nginx/sites-available/$DOMAIN"
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos \
    --email "admin@$DOMAIN" --redirect

echo ""
echo "============================================"
echo " DONE — https://$DOMAIN"
echo " ສ້າງ admin: sudo -u deploy $PY $APP_DIR/manage.py createsuperuser"
echo "============================================"
