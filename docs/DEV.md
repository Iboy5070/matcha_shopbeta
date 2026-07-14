# ພັດທະນາ Local (Development)

## ຄວາມຕ້ອງການ

- Python 3.11+
- Docker Desktop (ແນະນຳ — PostgreSQL local)
- Git

## ເລີ່ມໄວ (ແນະນຳ)

```bash
make run
```

Script `scripts/dev_run.sh` ຈະ:
1. ສ້າງ `.venv` + `pip install`
2. `docker compose up -d db` (ຖ້າ Docker ເປີດ)
3. `migrate`
4. `runserver` → http://127.0.0.1:8000/

## Setup ຄັ້ງທຳອິດ

```bash
git clone https://github.com/Iboy5070/matcha_shopbeta.git
cd matcha_shopbeta

cp .env.example .env
# ແກ້ .env ຕາມຕ້ອງການ (DATABASE_URL, BANK_*, etc.)

make run
```

ໃນ terminal ອື່ນ:

```bash
source .venv/bin/activate

# Admin (superuser) — ເຂົ້າ /admin/
python manage.py createsuperuser

# Staff — ເຂົ້າ /staff/ ແລະ /pos/
python manage.py create_staff

# ສິນຄ້າຕົວຢ່າງ (optional — ລຶບສິນຄ້າເກົ່າກ່ອນ seed!)
python seed_products.py
```

## Makefile

| Command | ໜ້າທີ່ |
|---------|--------|
| `make run` | migrate + runserver |
| `make db` | ເປີດ Postgres Docker |
| `make install` | venv + pip install |
| `make migrate` | django migrate |
| `make check` | django check |

## Database

### PostgreSQL (ແນະນຳ)

```bash
docker compose up -d db
```

`.env`:
```
DATABASE_URL=postgres://matcha:matcha@127.0.0.1:5432/matcha_shop
```

### SQLite (fallback)

ໃຊ້ເມື່ອ Docker ບໍ່ເປີດ ແລະ `DEBUG=True`:
- auto-fallback ໃນ `config/database.py`

ຫຼື ບັງຄັບ:
```
USE_SQLITE=1
```

**ຫຼີກລ້ຽງ SQLite** ຖ້າຢາກໃຊ້ Postgres ຕະຫຼອດ — ເປີດ Docker ກ່ອນ `make run`

### Production DB

**ຢ່າ** ໃຊ້ Supabase production `DATABASE_URL` ໃນ local — ແຍກ data ຊັດເຈນ

## URL Local

| | URL |
|---|-----|
| ຮ້ານ | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/login/ |
| Admin | http://127.0.0.1:8000/admin/ |
| Staff | http://127.0.0.1:8000/staff/ |
| POS | http://127.0.0.1:8000/pos/ |

## Management Commands

| Command | ໜ້າທີ່ |
|---------|--------|
| `createsuperuser` | Admin account |
| `create_staff` | Staff user (`--username`, `--password`, `--reset`) |
| `create_admin` | Admin helper (alternative) |
| `migrate` | DB migrations |
| `compilemessages` | compile .po → .mo (i18n) |
| `sync_catalog_i18n` | sync catalog translations |

## Env ສຳຄັນ (local)

```bash
DEBUG=True
DATABASE_URL=postgres://matcha:matcha@127.0.0.1:5432/matcha_shop
SITE_URL=http://127.0.0.1:8000

# Bank (ທົດ slip page)
BANK_NAME=BCEL
BANK_ACCOUNT_NUMBER=...
BANK_ACCOUNT_NAME=...
BANK_QR_IMAGE_URL=...
```

ເບິ່ງຄົບ: `.env.example`

## ແກ້ບັກທົ່ວໄປ

### PostgreSQL connection refused
```bash
docker compose up -d db
docker compose ps   # ກວດວ່າ db healthy
```

### Port 8000 ຖືກຈັບແລ້ວ
```bash
lsof -i :8000
kill <PID>
```

### Login ບໍ່ເຂົ້າ / ເຫັນ code ເກົ່າ
- ກວດວ່າ runserver ໃໝ່ຫຼັງ pull
- kill process ເກົ່າ (gunicorn/runserver ຄ້າງ)

### `shop_brand` / bank ວ່າງໃນ template
- ກວດ `config/context_processors.py` ຢູ່ใน `TEMPLATES` settings

### Static ບໍ່ຂຶ້ນ (prod)
```bash
python manage.py collectstatic --noinput
```

## ທົດ flow ຫຼັກ

1. Login customer → `/register/` → `/account/`
2. ເພີ່ມ cart → checkout buy → upload slip
3. Login staff → `/staff/slips/` → approve → stock ຫຼຸດ
4. Checkout reserve (ສິນຄ້າໝົດ) → staff approve → Admin ເຕີມ stock → `/staff/reserved/` complete

## ໂຄງສ້າງ code

ອ່ານ [ARCHITECTURE.md](ARCHITECTURE.md) ສຳລັບ flow stock, login, models
