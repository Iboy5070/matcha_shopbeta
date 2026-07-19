# ຄຳຖາມ-ຄຳຕອບດາຕ້າເບສ (ສອບບົດ / Demo)

> ໃຊ້ເວລາອາຈານຖາມກ່ຽວກັບ ER Diagram, Data Dictionary, PostgreSQL, Supabase  
> ໂຄງການ: **The 196 Haus Store Management System** — Django + PostgreSQL (Supabase)

---

## ຄຳຕອບ 1 ประโยค (ເປີດປาก)

> "ລະບົບໃຊ້ **PostgreSQL** 14 ຕາຕະລາງຕາມ ER ໃນບົດ — **logic ເດີຍກັນ**, ແຕ່ຕອນ implement ດ້ວູ **Django** ເພີ່ມ field ສຳລັບ login, stock, 3 ພາດາ, ແລະ cloud storage — ເປັນການຂະຫຍາຍ Physical Database ຈາກ Logical Design ໃນບົດ."

---

## ❌ ແກ້ code ໃຫ້ຄືກັບບົດ 100% ໄດ້ບໍ?

**ບໍ່ແນະນຳ** — ຈະພັງ web:

| ຖ້າແກ້ຕາມ PDF ຢ່າງເຄັ່ງ | ຜົນ |
|------------------------|-----|
| ເອົາ Password/Email ກັບໄປ Customer/Employee | ພັງ login, ລະຫັດບໍ່ hash, ຊ້ຳກັນ |
| ລຶບ `stock_qty`, `stock_ready` | ພັງ stock, reserve, checkout |
| ລຶບ i18n (name_th/en, slug) | ພັງ shop 3 ພາສາ, URL ສິນຄ້າ |
| `Img_path` ແທນ `slip_url` | slip ຫາຍເວລາ Render redeploy |
| Order ບັງຄັບ Emp_ID ຕອນ checkout | web order ສ້າງບໍ່ໄດ້ |

**ວິທີທີ່ຖືກ:** ເກັບ ER + Data Dictionary ໃນບົດ → **ອະທິບາຍວ່າ implement ເພີ່ມ field ໃດ ແລະ ເປັນຫຍັງ**

---

## ຕາຕະລາງປຽບທຽບ: ບົດ ↔ Django ↔ PostgreSQL

### ຊື່ຕາຕະລາງ

| ບົດ (ER) | Django Model | PostgreSQL table |
|----------|--------------|------------------|
| Employee | `Employee` | `store_employee` |
| Customer | `Customer` | `store_customer` |
| Supplier | `Supplier` | `inventory_supplier` |
| Category (Cas) | `Category` | `catalog_category` |
| Product | `Product` | `catalog_product` |
| Orders | `Order` | `sales_order` |
| Order_detail | `OrderItem` | `sales_orderitem` |
| Bill | `Bill` | `sales_bill` |
| Payment | `Payment` | `sales_payment` |
| Purchase_order | `PurchaseOrder` | `inventory_purchaseorder` |
| PO_detail | `PODetail` | `inventory_podetail` |
| Imports | `Imports` | `inventory_imports` |
| Import_detail | `ImportDetail` | `inventory_importdetail` |
| Inventory | `Inventory` | `inventory_inventory` |
| Reserved | `Reserved` | `sales_reserved` |

**+ ຕາຕະລາງ Django:** `auth_user` (login), `django_migrations`, ฯลฯ

---

### Employee / Customer

| ບົດ | Django | ຄຳອະທິບາຍຕອບອາຈານ |
|-----|--------|-------------------|
| Emp_ID, Email, Password | `id` + `auth_user` | Django ແຍກ **authentication** (login) ອອກຈາກ **profile** — ມາດຕະຐານ OWASP, password **hash** ບໍ່ເກັບ plain text |
| Cus_Name, Cus_Last | `cus_name`, `cus_last` | ຄືກັນ |
| user_id (FK) | — | ເຊື່ອມ Customer/Employee → User 1:1 |

**ຖ້າຖາມ:** "ເປັນຫຍັງ Password ບໍ່ຢູ່ຕາຕະລາງ Customer?"

> ເພາະ Django ໃຊ້ `auth_user` ຈັດການ login — ລະຫັດເກັບແບບ hash (PBKDF2) ປອດໄພກວ່າບົດທີ່ຂຽນ Password char(20). **Concept ເດີຍກັນ:** ລູກຄ້າມີ email + password ເພື່ອ login.

---

### Product / Category

| ບົດ | Django ເພີ່ມ | ເປັນຫຍັງ |
|-----|-------------|---------|
| Pro_Name, Price, Description, Img_path, Cas_ID | ✅ ຄືກັນ (`name`, `price`, `description`, `image`/`image_url`, `category_id`) | — |
| — | `stock_qty` | ຈັດການສະຕັອກ Ch.3 — ກວດກ່ອນຊື້, ຈອງໄດ້ເມື່ອໝົດ |
| — | `name_th`, `name_en`, `slug` | Ch.4 ຮູບ admin — ສິນຄ້າ 3 ພາສາ (ລາວ/ไทย/EN) |
| Cas_Name | + `name_th`, `name_en`, `slug` | URL `/product/...` ແລະ i18n |

---

### Orders / Bill / Payment

| ບົດ | Django | ໝາຍເຫດ |
|-----|--------|--------|
| Cus_ID NOT NULL | `customer_id` nullable | **Web order:** ລູກຄ້າສັ່ງ online ກ່ອນມີ staff → `employee_id` null ໄດ້ |
| Status ENUM | `PENDING, RESERVED, COMPLETED, CANCELLED` | ✅ ຄືກັນ |
| Bill Status | `PENDING, PARTIAL, PAID` | ✅ ຄືກັນ — PARTIAL ສຳລັບຈອງ (ມັດຈຳ 50%) |
| Img_path | `slip_url` (varchar URL) | Slip ຢູ່ **Supabase Storage** — ບໍ່ຫາຍເມື່ອ deploy Render |

**Flow ຕອບ demo:**

```
ລູກຄ້າ checkout → Order (PENDING) → Bill → Payment (slip_url)
→ Staff approve → Order COMPLETED → stock ຫຼຸດ
```

---

### Inventory / Reserved

| ບົດ | Django | ໝາຍເຫຼີ |
|-----|--------|--------|
| Inventory = batch ໃນສາງ | `inventory_inventory` | ທຸກຄັ້ນເຕີມສິນຄ້າ = 1 record |
| — | `Product.stock_qty` | **pool ຂายได้** — sum logic ຈາກ batch + reserve |
| Reserved 9 fields | + `stock_ready` | ເມື່ອເຕີມ stock → auto ຈັດໃຫ້ຈອງລ່າສຸດ |

**ຖ້າຖາມ:** "ມີ Inventory ແລ້ວເປັນຫຍັງຕ້ອງ stock_qty?"

> Inventory = **ລາຍລະອຽດ batch** (expiry, ວັນເຕີມ). `stock_qty` = **ຈຳນວນພ້ອມຂາຍ** ທີ່ web/POS ກວດ — ອອກແບບ 2 ຊັ້ນເພື່ອ performance ແລະ reserve logic.

---

## ຄຳຖາມທີ່ອາຈານມັກຖາມ + ຄຳຕອບ

### 1. ເປັນຫຍັງໃຊ້ PostgreSQL ບໍ່ແມ່ນ MySQL?

> PostgreSQL ເປັน open-source RDBMS ມາດຕະຐານ, Django ຮອງຮັບດີທີ່ສຸດ, Supabase ໃຫ້ PostgreSQL free tier. **SQL ແລະ ER ຄື MySQL ~95%** — ຕ່າງແຕ່ engine. ບົດອอกແບບ relational model; engine ເລືອກຕາມ framework.

### 2. Supabase ກັບ PostgreSQL ຕ່างກັນບໍ?

> **Supabase = PostgreSQL ຢູ່ cloud** + Storage + Auth API. Database engine ແມ່ນ Postgres ຈິງ — ເຊື່ອມດ້ວຍ `DATABASE_URL`. App ຢູ່ Render, DB ຢູ່ Supabase = **3-tier** (Presentation → Application → Data).

### 3. Docker ໃຊ້ເຮັດຫຍັງ?

> Local dev: `docker compose up -d db` → Postgres ເທົ່າກັນ prod. **ບໍ່ໃຊ້ SQLite ໃນ demo** — schema ເດີຍກັນ Supabase.

### 4. Normalization ເຖິງ FN ໃດ?

> **1NF:** atomic columns ✅  
> **2NF:** OrderItem, PODetail ແຍກຈາກ Order/PO ✅  
> **3NF:** Customer profile ≠ auth credentials (auth_user) ✅  
> Bill ແຍຈາກ Order — 1 order 1 bill, payments ຫຼายครั้ง → Bill.Paid_amount

### 5. Primary Key ໃຊ້ຫຍັງ?

> Django default: `id` BigAutoField auto-increment = Emp_ID, Pro_ID ໃນບົດ. **ຄວາມໝາຍເທົ່າກັນ**, ຊື່ column ຕ່າງ (convention framework).

### 6. Foreign Key ຕົວຢ່າງ?

> `sales_orderitem.product_id` → `catalog_product.id` (PROTECT — ບໍ່ລຶກ product ຖ້າມີ order)  
> `sales_order.customer_id` → `store_customer.id` (SET_NULL)

### 7. ENUM Status ມີຄ່າຫຍັງ?

| ຕາຕະລາງ | Values |
|---------|--------|
| Order | PENDING, RESERVED, COMPLETED, CANCELLED |
| Bill | PENDING, PARTIAL, PAID |
| Payment.pay_with | CASH, TRANSFER, QR |
| Reserved | RESERVED, PAID, COMPLETED, CANCELLED |
| PurchaseOrder | PENDING, COMPLETED, CANCELLED |

### 8. 1:M ຕົວຢ່າງ?

> Customer **1** → **M** Order  
> Order **1** → **M** OrderItem  
> Bill **1** → **M** Payment  
> Category **1** → **M** Product

### 9. 1:1 ຕົວຢ່າງ?

> Order **1** → **1** Bill (OneToOneField)

### 10. ຈອງ (Reserved) ເຮັດວຽກແນວໃດ?

> ລູກຄ້າ checkout ເລືອກ reserve → Order status RESERVED → Bill PARTIAL (ມັດຈຳ)  
> ສິນຄ້າໝົດກໍຈອງໄດ້ → ເຕີມ stock → `stock_ready=True` → staff complete → stock ຫຼຸດ

### 11. DFD D1–D11 ກົງກັບຕາຕະລາງບໍ?

| DFD Data Store | ຕາຕະລາງ |
|----------------|----------|
| D1 ສິນຄ້າ | catalog_product |
| D2 ໝວດໝູ່ | catalog_category |
| D3 ພະນັກງານ | store_employee + auth_user |
| D4 ລູກຄ້າ | store_customer + auth_user |
| D5 ຜູ້ສະໜອງ | inventory_supplier |
| D6 ການຊື້ | sales_order + sales_orderitem |
| D7 ການຈອງ | sales_reserved |
| D8 ຊຳລະ | sales_payment |
| D9 ສັ່ງຊື້ເຂົ້າ | inventory_purchaseorder |
| D10 ນຳເຂົ້າ | inventory_imports |
| D11 ສະຕັອກ | inventory_inventory + stock_qty |

---

## Demo ຖ້າອາຈານຂໃຫ້ເບິ່ງ DB

### Supabase Dashboard

1. **Table Editor** → ເປີດ `catalog_product`, `sales_order`, `sales_reserved`
2. **SQL Editor:**

```sql
-- ສິນຄ້າ + stock
SELECT id, name, price, stock_qty FROM catalog_product;

-- Order ລ່າສຸດ
SELECT o.id, o.status, c.cus_name, b.total_amount, b.status AS bill_status
FROM sales_order o
LEFT JOIN store_customer c ON c.id = o.customer_id
LEFT JOIN sales_bill b ON b.order_id = o.id
ORDER BY o.id DESC LIMIT 5;
```

### Django Admin

> `/admin/` → ເບິ່ງ Products (stock_qty), Orders, Reserved, Inventory batches

### Local script

```bash
DATABASE_URL="postgres://...@db....supabase.co:5432/postgres" \
  python scripts/check_db_schema.py
```

---

## ສິ່ງທີ່ຄວນແກ້ໃນ **ບົດ Word** (ບໍ່ແກ່ code)

1. **Ch.3 Data Relation** — ແກ້ Payment block ທີ່ລວມ PO_ID (ຜິດ copy-paste)
2. **Ch.3.7 Product** — ເພີ່ມແຖວ `stock_qty` ໃນ Data Dictionary
3. **Ch.3.11 Payment** — `Img_path` → `slip_url` (URL cloud)
4. **Ch.3.17 Reserved** — ເພີ່ມ `stock_ready`, ແກ້ description Res_ID
5. **Ch.5 ຈຸດອ່ອນ** — ລຶບ/ແກ້: buy+reserve ໃນ checkout ✅, login email ✅
6. **Appendix** — ຕາຕະລາງ mapping ບົດ↔Django (copy ຈາກເອກະສານນີ້)

---

## ສະຫຼຸບສຳລັບປິດຄຳຖາມ

| ຄຳຖາມ | ຄຳຕອບສັ້ນ |
|-------|-----------|
| DB ກົງບົດບໍ? | **Logic + ER ກົງ** — 14 entity, FK, status ຄືກັນ |
| ຊື່ column ກົງບໍ? | **Concept ກົງ** — Django ໃຊ້ snake_case + id |
| ເພີ່ມ field ຜິດບໍ? | **ບໍ່** — physical extension ຕາມ Django + cloud + stock |
| ເປັນຫຍັง Supabase? | Hosted PostgreSQL + slip storage |
| ເປັນຫຍັງ Django? | ORM, admin, auth, security — Ch.2.3.6 |

**ປະໂຫຍກນຳ:** "Logical design ຢູ່ໃນບົດ; physical implementation ຂະຫຍາຍເພື່ອ security, i18n, ແລະ deployment ຈິງ — ນີ້ແມ່ນຂั้นตอນ Implementation ຕາມ SDLC."

---

## ໄຟລອ້າງອີງໃນ repo

| ໄຟລ | ເນື້ອໃນ |
|-----|---------|
| `docs/THESIS_CH3_P37-45.md` | ER + Data Dictionary sync Django |
| `apps/*/models.py` | Source of truth |
| `scripts/check_db_schema.py` | ກວດ Supabase vs Django |
