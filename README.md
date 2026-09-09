# The 196 Haus Matcha — Local Demo

> ໂຄງການນີ້ເປັນ Prototype/Local Demo ສຳລັບການສຶກສາ.
> ຍັງບໍ່ແມ່ນເວັບ Production ແລະບໍ່ໃຊ້ຮັບການຊຳລະເງິນຈິງ.

ລະບົບຮ້ານຂາຍມັດຊະ: ຮ້ານອອນລາຍ, ສັ່ງຊື້, ຈອງສິນຄ້າ,
ກວດສະລິບ, POS, ສາງສິນຄ້າ ແລະລາຍງານ.

## ເປີດ Demo ແບບງ່າຍ

ຕ້ອງຕິດຕັ້ງ [Python 3](https://www.python.org/downloads/) ກ່ອນ.
ການເປີດຄັ້ງທຳອິດຕ້ອງມີ Internet ແລະອາດໃຊ້ເວລາ 2–5 ນາທີ.
ຄັ້ງຕໍ່ໄປຈະເປີດໄວ ແລະໃຊ້ງານແບບ Offline ໄດ້.

### Mac

1. Double-click `RUN_DEMO.command`
2. ຖ້າ Mac ບລັອກ: ຄລິກຂວາໄຟລ໌ → **Open** → **Open**
3. Browser ຈະເປີດໜ້າຮ້ານອັດຕະໂນມັດ

### Windows

1. Double-click `RUN_DEMO_WINDOWS.bat`
2. Browser ຈະເປີດໜ້າຮ້ານອັດຕະໂນມັດ

ຢ່າປິດໜ້າ Terminal ໃນຂະນະໃຊ້ Demo. ກົດ `Control + C`
ໃນ Terminal ເມື່ອຕ້ອງການຢຸດ.

## ທີ່ຢູ່ ແລະບັນຊີທົດສອບ

- ໜ້າຮ້ານ: http://127.0.0.1:8000/
- Staff/POS: http://127.0.0.1:8000/staff/
  - Username: `staff`
  - Password: `StaffMatcha2026!`
- Admin: http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `AdminMatcha2026!`

Demo ໃນ ZIP ໃຊ້ຖານຂໍ້ມູນ `db.sqlite3` ໃນເຄື່ອງ ຈຶ່ງບໍ່ຊ້າ
ແລະບໍ່ຕ້ອງຕິດຕັ້ງ PostgreSQL ຫຼື Docker.

## Source code

https://github.com/Iboy5070/matcha_shopbeta

ໃຫ້ໃຊ້ Local Demo ໃນ ZIP ເປັນຫຼັກ. ລິ້ງ Render ຍັງບໍ່ເປີດ
ໃຫ້ໃຊ້ເປັນເວັບຈິງ.

## ຖ້າເປີດບໍ່ໄດ້

- ຂຶ້ນ `python: command not found`: ຕິດຕັ້ງ Python 3 ແລ້ວເປີດໄຟລ໌ Demo ໃໝ່.
- Port 8000 ຖືກໃຊ້: ປິດ Terminal ເກົ່າທີ່ກຳລັງເປີດ Demo.
- ຄັ້ງທຳອິດຕິດຕັ້ງບໍ່ສຳເລັດ: ກວດ Internet ແລ້ວເປີດອີກຄັ້ງ.

## ສຳລັບນັກພັດທະນາ

```bash
make run
```

Production ໃຊ້ PostgreSQL ຜ່ານ `DATABASE_URL`. ຄ່າຕັ້ງຕ່າງໆເບິ່ງໃນ
`.env.example`.
