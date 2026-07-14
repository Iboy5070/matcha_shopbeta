# ເອກະສານໂປຣເຈັກ MATCHAZUKI

Django e-commerce shop — **The 196 Haus Matcha** (ພາສາລາວເປັນຫຼັກ, lo/en/th)

## ເອກະສານຫຼັກ

| ໄຟລ | ໃຊ້ເມື່ອ |
|-----|----------|
| [DEV.md](DEV.md) | ຕັ້ງເຄື່ອງ local, run, migrate, seed, ແກ້ບັກ |
| [ARCHITECTURE.md](ARCHITECTURE.md) | ເຂົ້າໃຈໂຄງສ້າງ app, model, flow, ໄຟລສຳຄັນ |
| [DEPLOY.md](DEPLOY.md) | ອັບ Render, Supabase, env, wake page |

## URL ສຳຄັນ

| ບ່ອນ | Local | Production |
|------|-------|------------|
| ຮ້ານ | http://127.0.0.1:8000/ | https://iboy5070.github.io/matcha_shopbeta/ (wake page) |
| Login | /login/ | /login/ |
| Admin | /admin/ (superuser) | /admin/ |
| Staff | /staff/ | /staff/ |
| POS | /pos/ | /pos/ |
| Health | /healthz/ | /healthz/ |

## ໂຄງສ້າງໂຟລເດີ

```
matcha_shopbeta/
├── apps/
│   ├── store/       # ຮ້ານ, cart, checkout, login, account
│   ├── catalog/     # ສິນຄ້າ, category, stock_qty
│   ├── sales/       # POS, orders, staff portal
│   └── inventory/   # ສາງ, PO, import, batch stock
├── config/          # settings, database, urls, admin branding
├── templates/       # HTML (store/, staff/, admin/, pos)
├── static/          # CSS, JS, ຮູບສິນຄ້າ
├── docs/            # ເອກະສານນີ້ + wake page (index.html)
├── deploy/          # env production, Cloudflare worker
└── scripts/         # dev_run.sh
```

## ສຳລັບ AI / Cursor

- Rule ອັດຕະໂນມັດ: `.cursor/rules/matchazuki-project.mdc`
- ອ່ານ **ARCHITECTURE.md** ກ່ອນແກ້ stock, checkout, ຫຼື reservation
- ອ່ານ **DEV.md** ກ່ອນແກ້ local run / database
- ອ່ານ **DEPLOY.md** ກ່ອນແກ້ production / env

## GitHub

https://github.com/Iboy5070/matcha_shopbeta
