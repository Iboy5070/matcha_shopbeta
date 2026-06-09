# Matcha Shop Beta

Django store inspired by [MATCHAZUKI](https://matchazuki.com/) with PostgreSQL, bilingual TH/EN storefront, and POS for staff.

## Requirements

- Python 3.11+
- Docker (for PostgreSQL) or your own Postgres server

## Setup

```bash
git clone <repo_url>
cd matcha_shopbeta

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Start PostgreSQL (requires Docker Desktop running)
docker compose up -d db

# Wait until the db container is healthy, then migrate
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # optional sample FAQ & testimonials
python manage.py compilemessages

python manage.py runserver
```

- Storefront: http://127.0.0.1:8000/
- POS (staff): http://127.0.0.1:8000/pos/
- Admin: http://127.0.0.1:8000/admin/

## Database

Default connection uses **PostgreSQL** via `DATABASE_URL` (see `.env.example`).

```bash
docker compose up -d db
```

To use another Postgres host, set `DATABASE_URL` in `.env`, for example:

```
postgres://USER:PASSWORD@HOST:5432/DATABASE
```

## Environment

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts |
| `DATABASE_URL` | PostgreSQL connection URL |
| `CONTACT_EMAIL` | Shown on contact/footer |
| `WHATSAPP_PHONE` | Lao number with country code, e.g. `8562012345678` (auto-builds `wa.me` link) |
| `WHATSAPP_URL` | Full WhatsApp link (optional; overrides `WHATSAPP_PHONE`) |
| `FACEBOOK_URL` | Facebook page or Messenger link |
| `LINE_URL` | LINE official account link |

## Content

Manage products, images, categories, testimonials, and FAQ in Django admin.

## Free tier (Render)

Render free sleeps after ~15 minutes idle. This repo includes:

- **`/healthz/`** — lightweight health check
- **`.github/workflows/keep-warm.yml`** — pings every 5 minutes (auto after push)
- **`docs/index.html`** — wake page for mobile (enable GitHub Pages once)

### One-time setup (GitHub Pages)

1. GitHub repo → **Settings** → **Pages**
2. Source: branch **main**, folder **/docs** → Save
3. Share this link on Facebook/LINE (not the Render URL directly):

   `https://iboy5070.github.io/matcha_shopbeta/`

Optional: [UptimeRobot](https://uptimerobot.com) monitor on `https://matcha-shopbeta.onrender.com/healthz/` every 5 min as backup.
