# Deploy Production

## Overview

| ສ່ວນ | Platform |
|------|----------|
| Web app | [Render](https://render.com) free tier |
| Database | [Supabase](https://supabase.com) PostgreSQL |
| Slip storage | Supabase Storage (bucket `slips`) |
| Wake page | GitHub Pages (`docs/index.html`) |
| Keep-warm | GitHub Actions (`.github/workflows/keep-warm*.yml`) |

## URLs

| | URL |
|---|-----|
| App (direct) | https://matcha-shopbeta.onrender.com |
| **Share link** | https://iboy5070.github.io/matcha_shopbeta/ |
| Health | https://matcha-shopbeta.onrender.com/healthz/ |
| GitHub | https://github.com/Iboy5070/matcha_shopbeta |

**ແຊร์ wake page URL** — Render free tier sleep ~15 ນາທີ, wake page auto-retry

## Render Setup

1. Connect GitHub repo → Web Service
2. Build: nixpacks (auto from repo)
3. Start: `scripts/render_start.sh` (migrate + gunicorn)
4. Environment: copy from `deploy/env.production.example`

### Env ບັງຄັບ (production)

```
SECRET_KEY=<random-long-string>
DEBUG=0
ALLOWED_HOSTS=matcha-shopbeta.onrender.com
DATABASE_URL=postgres://...@db....supabase.co:5432/postgres

SITE_URL=https://matcha-shopbeta.onrender.com
WAKE_PAGE_URL=https://iboy5070.github.io/matcha_shopbeta/

BANK_NAME=BCEL
BANK_ACCOUNT_NUMBER=...
BANK_ACCOUNT_NAME=...
BANK_QR_IMAGE_URL=https://... (URL ຮູບ QR ຈິງ)

CONTACT_EMAIL=...
NOTIFY_EMAIL=...
WHATSAPP_PHONE=85620...
```

### Supabase Storage (slips)

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_KEY=<service_role key>
SUPABASE_SLIP_BUCKET=slips
```

Dashboard → Storage → New bucket `slips` → Public

## Deploy Checklist

```bash
# Local ກ່ອນ push
make check
python manage.py migrate --plan

# ຫຼັງ deploy ໃນ Render Shell (ຖ້າມີ)
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

- [ ] `DEBUG=0`
- [ ] `DATABASE_URL` = Supabase (ບໍ່ແມ່ນ local Docker)
- [ ] `BANK_*` ຕັ້ງຄົບ — ບໍ່ມີ warning placeholder
- [ ] `SITE_URL` = Render URL
- [ ] Migrate ແລ້ວ (`stock_qty` column, etc.)
- [ ] GitHub Pages enabled (main / docs)
- [ ] Keep-warm workflow active

## GitHub Pages (Wake Page)

1. Repo → **Settings** → **Pages**
2. Branch: **main**, folder: **/docs**
3. Share: `https://iboy5070.github.io/matcha_shopbeta/`

Wake page (`docs/index.html`) ping `/healthz/` ແລະ auto-retry ເມື່ອ Render sleep

## Keep Warm

`.github/workflows/keep-warm.yml` + `keep-warm-offset.yml`  
Ping `/healthz/` ~ທຸກ 2 ນາທີ — ຊ່ວຍຫຼຸດ cold start

Backup: [cron-job.org](https://cron-job.org) → GET `/healthz/` every 1 min

## Cloudflare Worker (optional — UX ດີກວ່າ)

1. Cloudflare → Workers → paste `deploy/cloudflare-worker/worker.js`
2. Variable `ORIGIN` = `https://matcha-shopbeta.onrender.com`
3. Share `https://YOUR-NAME.workers.dev`

## Link Quality

| Link | UX |
|------|-----|
| Cloudflare Worker | ດີທີ່ສຸດ — server-side retry |
| GitHub Pages wake | ດີ — browser auto-retry |
| Render direct | ຊ້າ — ອາດຕ້ອງ reload |

## Post-Deploy Test

1. ເປີດ wake page → ຮ້ານໂຫຼດ
2. Login customer + staff
3. Checkout → bank QR ຂຶ້ນ → upload slip
4. Staff approve → stock ຫຼຸດ
5. `/healthz/` → 200 OK

## Troubleshooting

| ບັກ | ແກ້ |
|-----|-----|
| 502 / sleep | ລໍ wake page retry ຫຼື keep-warm |
| Static ບໍ່ຂຶ້ນ | `collectstatic`, WhiteNoise enabled |
| CSRF error | `CSRF_TRUSTED_ORIGINS` in settings (Render auto) |
| DB error | ກວດ `DATABASE_URL`, Supabase IP allow |
| Slip upload fail | `SUPABASE_*` env + bucket public |

## Local vs Production

| | Local | Production |
|---|-------|------------|
| DB | Docker Postgres | Supabase |
| DEBUG | True | False |
| Static | Django dev | WhiteNoise |
| Share URL | localhost | Wake page |

ອ່ານ [DEV.md](DEV.md) ສຳລັບ local setup
