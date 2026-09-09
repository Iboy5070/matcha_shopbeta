# ລະບົບຮ້ານ The 196 Haus Matcha

ໂປຣແກຣມຮ້ານຂາຍມັດຊະ: ໜ້າຮ້ານອອນລາຍ, ຮັບອໍເດີ, ກວດສະລິບ,
ຂາຍຜ່ານ POS, ຈັດການສາງ ແລະພິມລາຍງານ.

## ຄູ່ມືສຳລັບອາຈານ

### 1. ກ່ອນເປີດ

ເຄື່ອງຕ້ອງມີ [Python 3](https://www.python.org/downloads/).
ຄັ້ງທຳອິດຕ້ອງຕໍ່ Internet ແລະລໍຖ້າປະມານ 2–5 ນາທີ.
ຫຼັງຈາກຕິດຕັ້ງຄັ້ງທຳອິດແລ້ວ ຄັ້ງຕໍ່ໄປຈະເປີດໄວ.

### 2. ເປີດໂປຣແກຣມ

- Mac: ເປີດ Terminal ໃນໂຟລເດີໂປຣແກຣມ ແລ້ວພິມ `./RUN_DEMO.command`
  - ຖ້າຂຶ້ນ `Permission denied` ໃຫ້ພິມ `chmod +x RUN_DEMO.command` ແລ້ວພິມ `./RUN_DEMO.command` ອີກຄັ້ງ
- Windows: double-click ໄຟລ໌ `RUN_DEMO_WINDOWS.bat`

ລໍຖ້າໃຫ້ Browser ເປີດໜ້າ http://127.0.0.1:8000/ ອັດຕະໂນມັດ.
ຢ່າປິດໜ້າ Terminal ໃນຂະນະໃຊ້ໂປຣແກຣມ.

### 3. ເຂົ້າລະບົບ

ບັນຊີຂ້າງລຸ່ມໃຊ້ສຳລັບໂປຣແກຣມໃນ ZIP ເທົ່ານັ້ນ.
ຕ້ອງພິມຕົວໃຫຍ່-ຕົວນ້ອຍໃຫ້ຖືກ ແລະບໍ່ໃສ່ຊ່ອງວ່າງ.

- ພະນັກງານ (Staff/POS)
  - ເຂົ້າທີ່: http://127.0.0.1:8000/staff/
  - ຊື່ຜູ້ໃຊ້: `staff`
  - ລະຫັດຜ່ານ: `StaffMatcha2026!`
  - ໃຊ້ສຳລັບ: ຂາຍສິນຄ້າ, ເບິ່ງອໍເດີ, ກວດສະລິບ ແລະເບິ່ງລາຍງານ

- ຜູ້ຄຸ້ມຄອງ (Admin)
  - ເຂົ້າທີ່: http://127.0.0.1:8000/admin/
  - ຊື່ຜູ້ໃຊ້: `admin`
  - ລະຫັດຜ່ານ: `AdminMatcha2026!`
  - ໃຊ້ສຳລັບ: ຈັດການສິນຄ້າ, ຜູ້ໃຊ້, ອໍເດີ ແລະສາງ

### 4. ປິດໂປຣແກຣມ

ກັບໄປທີ່ໜ້າ Terminal ແລ້ວກົດ `Control + C`.

## ສຳລັບຜູ້ກວດສອບ / For reviewers

| | Link |
|--|------|
| **ເຂົ້າເບິ່ງລະບົບ (demo)** | https://iboy5070.github.io/matcha_shopbeta/ |
| **Source code (GitHub)** | https://github.com/Iboy5070/matcha_shopbeta |

> ໃຊ້ **demo link ຂ້າງເທິງ** (wake page) — ລໍສອງສາມວິນາທີຖ້າ server ກຳລັງຕື່ນ (Render free tier). ຢ່າໃຊ້ Render URL ໂດຍກົງ.

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/index.html](docs/index.html) | Wake page (GitHub Pages demo) |

## Requirements

- Python 3.11+
- Docker (for PostgreSQL) or your own Postgres server

## Quick start (local)

```bash
make run
```

This will:
- create `.venv` if needed
- start PostgreSQL via Docker (if Docker is running)
- fall back to **SQLite** (`db.sqlite3`) if Postgres is unavailable
- run migrations and start `runserver` at http://127.0.0.1:8000/

Without Docker: add `USE_SQLITE=1` to `.env` or just run `make run` (auto-fallback when `DEBUG=1`).

## Setup (manual)

```bash
git clone https://github.com/Iboy5070/matcha_shopbeta.git
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
python seed_products.py      # optional sample products (clears existing catalog)
python manage.py create_staff
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
- **`.github/workflows/keep-warm.yml`** + **`keep-warm-offset.yml`** — ping ~every 2 minutes (auto)
- **`docs/index.html`** — wake page with **automatic retry** (no manual reload)
- **`deploy/cloudflare-worker/worker.js`** — optional best fix (server-side retry)

### Link quality (best → worst)

| Link | Experience |
|------|------------|
| Cloudflare Worker `*.workers.dev` | Best — server retries for you |
| GitHub Pages wake URL | Good — auto-retry in browser |
| Render URL direct | Worst — may need manual reload |

### One-time setup (GitHub Pages)

1. GitHub repo → **Settings** → **Pages** → branch **main**, folder **/docs** → Save
2. Share on Facebook/LINE:

   `https://iboy5070.github.io/matcha_shopbeta/`

   Optional query params: `?wa=85620XXXXXXXX&fb=https://facebook.com/yourpage`

### Optional: Cloudflare Worker (best free UX)

1. [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers → Create → paste `deploy/cloudflare-worker/worker.js`
2. Add variable `ORIGIN` = `https://matcha-shopbeta.onrender.com`
3. Share your `https://YOUR-NAME.workers.dev` link instead

Backup ping: [cron-job.org](https://cron-job.org) every **1 minute** → `/healthz/`
