# ໂຄງສ້າງລະບົບ (Architecture)

## Stack

| ຊັ້ນ | ເທັກ |
|------|-----|
| Backend | Django 4.2, Python 3.11+ |
| Database | PostgreSQL (Supabase prod, Docker local) |
| Admin UI | django-unfold |
| Static | WhiteNoise |
| Deploy | Render (free tier), nixpacks |
| Storage | Supabase Storage (slip upload, optional) |
| Payment | BCEL bank transfer + QR + upload slip |

## Django Apps

| App | ໜ້າທີ່ | ໄຟລສຳຄັນ |
|-----|--------|-----------|
| `apps/store` | Storefront, cart, checkout, auth, account, FAQ/blog | `views.py`, `forms.py`, `urls.py` |
| `apps/catalog` | Product, Category, `stock_qty` | `models.py`, `stock.py`, `admin.py` |
| `apps/sales` | Order, Bill, Payment, Reserved, POS, staff portal | `models.py`, `views.py`, `staff_views.py` |
| `apps/inventory` | Supplier, PO, Import, Inventory batches | `models.py` |

## Models ຫຼັກ

```
Customer (store) ──< Order (sales) ──< OrderItem ──> Product (catalog)
                      │
                      ├── Bill ──< Payment
                      └── Reserved ──> Product

Product.stock_qty     ← pool ທີ່ຂາຍ/ຈອງໄດ້
Inventory (batch)     ← ລາຍການສາງ (ເຕີມສິນຄ້າ, FIFO ເວລາຂາຍ)
```

### Order status
- `PENDING` — ລໍຖ້າຊຳລະ
- `RESERVED` — ຈອງ (ມັດຈຳ)
- `COMPLETED` — ສຳເລັດ
- `CANCELLED` — ຍົກເລີກ

### Bill status
- `PENDING` / `PARTIAL` / `PAID`

### Reserved status
- `RESERVED` → `COMPLETED` / `CANCELLED`
- `stock_ready` — ສິນຄ້າຖືກຈັດໃຫ້ການຈອງແລ້ວ (auto ເມື່ອເຕີມ stock)

## URL Routes

### Store (`apps/store/urls.py`)
- `/` — ໜ້າຫຼັກ
- `/shop/`, `/product/<id>/` — ສິນຄ້າ
- `/cart/`, `/checkout/` — ກະຕ່າ, ຊຳລະ
- `/order/<id>/pay/` — ອັບໂຫຼດ slip
- `/login/`, `/register/`, `/account/` — auth + profile

### Sales (`apps/sales/urls.py`)
- `/pos/` — Point of Sale
- `/staff/` — dashboard
- `/staff/slips/` — ກວດ slip
- `/staff/reserved/` — ຈັດການຈອງ
- `/staff/inventory/` — ເບິ່ງ stock (read-only)

### Config (`config/urls.py`)
- `/admin/` — Django Admin (superuser only)
- `/healthz/` — health check
- `/i18n/setlang/` — ປ່ຽນພາສາ

## Login ແບບລວມ (Unified Login)

**ຈຸດເຂົ້າດຽວ:** `/login/` (modal ຫຼື ໜ້າ login)

| ປະເພດ user | Redirect ຫຼັງ login |
|------------|---------------------|
| superuser | `/admin/` |
| staff (`is_staff`) | `/staff/` |
| customer | `/` ຫຼື `?next=` |

- `/admin/login/` → redirect ໄປ `/login/`
- `/staff/login/` → redirect ໄປ `/login/`
- Middleware: `AdminSuperuserOnlyMiddleware` — ບໍ່ໃຫ້ staff ເຂົ້າ admin

## Flow: ຊື້ອອນໄລນ (Buy Now)

```
ລູກຄ້າ → cart → checkout (order_type=buy)
         → check_stock() — ຖ້າໝົດ = ບໍ່ໃຫ້ຊື້, ແຕ່ຈອງໄດ້
         → Order + Bill (PENDING)
         → /order/<id>/pay/ — ໂອນ + upload slip
         → staff /staff/slips/ → approve
         → deduct_stock() — ຫຼຸດ stock_qty + Inventory batch
         → Order COMPLETED, Bill PAID
```

**ສຳຄັນ:** stock **ບໍ່** ຫຼຸດຕອນ checkout — ຫຼຸດຕອນ staff approve ເທົ່ານັ້ນ

## Flow: ຈອງ (Reserve)

```
ລູກຄ້າ → checkout (order_type=reserve, ມັດຈຳ ~50%)
         → Order (RESERVED) + Reserved record
         → upload slip (ມັດຈຳ)
         → staff approve slip
         → ເມື່ອເຕີມ stock (Inventory/ImportDetail save)
            → receive_stock() → ຈັດໃຫ້ຈອງລ່າສຸດກ່ອນ (stock_ready=True)
         → staff /staff/reserved/ → Complete
            → consume_allocated_stock() ຖ້າ stock_ready
            → deduct_stock() ຖ້າຍັງບໍ່ມີ stock
         → Cancel → release_stock() ຖ້າ stock_ready
```

## Flow: POS

- **Buy now:** `pos_checkout` → deduct stock ທັນທີ (staff ຢືນຢັນໃນເຄື່ອ)
- **Reserve:** `/pos/reserve/` → ມັດຈຳ + Reserved record

## Stock Logic (`apps/catalog/stock.py`)

| Function | ເມື່ອໃຊ້ |
|----------|----------|
| `check_stock()` | checkout buy-now — ກວດວ່າພໍບໍ່ |
| `deduct_stock()` | staff approve slip, POS buy, complete reserve (no earmark) |
| `receive_stock()` | ເຕີມສິນຄ້າໃໝ່ + auto-allocate reservations |
| `consume_allocated_stock()` | complete reserve ທີ່ stock_ready ແລ້ວ |
| `release_stock()` | cancel reserve ທີ່ stock_ready |

Trigger ເຕີມ stock:
- `Inventory.save()` (new batch)
- `ImportDetail.save()` (import)

## Context ໃນ Template

`config/context_processors.py` → `site_context`  
ສົ່ງ: `shop_brand`, `bank_name`, `bank_qr_image_url`, contact links, etc.

## i18n

- Default: `lo` (Lao)
- Languages: lo, en, th
- Locale: `locale/*/LC_MESSAGES/django.po`
- Catalog i18n: `sync_catalog_i18n` command

## ໄຟລ config ສຳຄັນ

| ໄຟລ | ໜ້າທີ່ |
|-----|--------|
| `config/settings.py` | env, i18n, UNFOLD, LOGIN_URL |
| `config/database.py` | Postgres + SQLite fallback (DEBUG only) |
| `config/admin_branding.py` | Admin login → store login |
| `config/health.py` | /healthz/ + CORS wake page |
| `config/context_processors.py` | template globals |
