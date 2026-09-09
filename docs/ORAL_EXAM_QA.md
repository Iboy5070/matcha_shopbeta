# The 196 Haus MATCHA — Oral Exam Q&A

> ຄຳຖາມ–ຄຳຕອບສຳລັບໂຊອາຈານ (ເນັ້ນ DB + ຄຳຖາມສໍ້)

## ຕອບໃນ 20 ວິນາທີ

ລະບົບໃຊ້ **Django + PostgreSQL**: ຄົນ (User/Employee/Customer) → ຂາຍ (Order/OrderItem/Bill/Payment/Reserved) → ສິນຄ້າ (Category/Product.stock_qty) → ສາງ (Supplier→PO→Import→Inventory). ເວັບຕັດ stock **ຫລັງ staff ອະນຸມັດສະລິບ**; POS ຕັດ **ທັນທີ**.

## ER ສັ້ນ

```
User 1:1 Employee
User 1:1? Customer
Customer/Employee --> Order
Order 1:N OrderItem --> Product (PROTECT)
Order 1:1 Bill 1:N Payment (+ slip_url)
Order 1:N Reserved
Category 1:N Product.stock_qty
Supplier --> PO --> Import --> receive_stock --> Product + Inventory (FIFO)
```

## 1) Database basics

### Q1. ລະບົບນີ້ໃຊ້ຖານຂໍ້ມູນຫຍັງ? ເປັນຫຍັງເລືອກມັນ?

**A:** Production ໃຊ້ PostgreSQL (Supabase + DATABASE_URL). Local ໃຊ້ Postgres ໃນ Docker ຫລື fallback SQLite ເມື່ອ DEBUG=1. ເລືອກ Postgres ເພາະຮອງ concurrent, integrity, ແລະ deploy.

### Q2. ORM ແມ່ນຫຍັງ? ໂປຣເຈັກໃຊ້ຫຍັງ?

**A:** ORM = Object-Relational Mapping — ໃຊ້ Model ແທນຂຽນ SQL ດິບ. ໂປຣເຈັກໃຊ້ Django ORM.

### Q3. Primary Key / Foreign Key ແມ່ນຫຍັງ? ຍົກຕົວຢ່າງ

**A:** PK = ລະຫັດຫລັກ (id). FK = ຊີ້ໄປ PK ຕາຕະລາງອື່ນ. ຕົວຢ່າງ: OrderItem.order → Order, Payment.bill → Bill, Product.category → Category.

### Q4. OneToOne ກັບ ForeignKey ແຕກຕ່າງກັນແນວໃດ?

**A:** FK = ຫລາຍແຖວຊີ້ໄປ 1 ແຖວໄດ້. OneToOne = ຄູ່ 1:1. ໃນລະບົບ: Bill–Order; Employee.user / Customer.user → User.

### Q5. ຕາຕະລາງຫລັກມີຫຍັງແນ່?

**A:** ຄົນ: Employee, Customer, User. ສິນຄ້າ: Category, Product. ຂາຍ: Order, OrderItem, Bill, Payment, Reserved. ສາງ: Supplier, PurchaseOrder, PODetail, Imports, ImportDetail, Inventory.

### Q6. ເປັນຫຍັງແຍກ Order ກັບ OrderItem?

**A:** 1 ອໍເດີມີຫລາຍສິນຄ້າ (1:N). OrderItem ເກັບ product, quantity, price, subtotal ຂອງແຕ່ລະແຖວ — ຫລຸດຂໍ້ມູນຊ້ຳ.

### Q7. ເປັນຫຍັງມີທັງ Order ແລະ Bill?

**A:** Order = ລາຍການສັ່ງ + status. Bill = ໃບບິນເງິນ (total/paid/balance) 1:1 ກັບ Order. Payment ຫລາຍຄັ້ງຕໍ່ 1 Bill ໄດ້.

### Q8. Normalization ແມ່ນຫຍັງ?

**A:** ແຍກຂໍ້ມູນເພື່ອຫລຸດຊ້ຳ. ຊື່ສິນຄ້າຢູ່ Product; ລາຄາຂາຍເກັບໃນ OrderItem ເປັນ snapshot ເພາະລາຄາອາດປ່ຽນພາຍຫລັງ.

### Q9. CASCADE / PROTECT / SET_NULL ແມ່ນຫຍັງ?

**A:** CASCADE: ລຶບແມ່ → ລຶບລູກ. PROTECT: ຫ້າມລຶບຖ້າມີອ້າງອີງ (Product ໃນ OrderItem). SET_NULL: ຕັ້ງ FK = null.

### Q10. Stock ເກັບຢູ່ໃສ?

**A:** 1) Product.stock_qty = ຈຳນວນຂາຍໄດ້. 2) Inventory = batch ສາງ. ນຳເຂົ້າ → receive_stock; ຂາຍ → deduct + FIFO.

### Q11. Migration ແມ່ນຫຍັງ?

**A:** ໄຟລ໌ປ່ຽນໂຄງສ້າງ DB ຕາມ Model. makemigrations = ສ້າງໄຟລ໌, migrate = ນຳໃຊ້ກັບ DB.

## 2) Tricky DB (HOT)

### Q12. ເວັບຊື້ດຽວນີ້ ຕັດ stock ຕອນໃດ? ເປັນຫຍັງບໍ່ຕັດຕອນ checkout?

**A:** ຕັດຕອນ staff ອະນຸມັດສະລິບເທົ່ານັ້ນ. Checkout ພຽງ check_stock. ເພາະຍັງບໍ່ຈ່າຍຈິງ — ຖ້າຕັດທັນທີຈະຂັດສະຕັອກຈາກຄົນທີ່ບໍ່ໂອນເງິນ.

> **HOT** — ຄຳຖາມສໍ້ຍອດນິຍົມ ຈື່ໃຫ້ຂຶ້ນໃຈ!

### Q13. POS ຂາຍໜ້າຮ້ານ ຕັດ stock ຕອນໃດ?

**A:** POS ຕັດທັນທີເມື່ອສຳເລັດບິນ (ຮັບເງິນແລ້ວ). ເວັບລໍຢືນຢັນສະລິບກ່ອນ.

### Q14. ສອງຄົນສັ່ງພ້ອມກັນ (race condition) ຈະເກີດຫຍັງ?

**A:** ອາດ oversell ຖ້າບໍ່ກວດ/ຕັດ stock ໃນ transaction. ຕ້ອງ atomic + ກວດພ້ອມກັນຕັດ.

### Q15. Reserved ແຕກຕ່າງຈາກ Order ປົກກະຕິແນວໃດ?

**A:** ມີຕາຕະລາງ Reserved: deposit, remain, expire_at, stock_ready. ຈ່າຍມັດຈຳກ່ອນ ຮັບເຄື່ອງພາຍຫລັງ.

### Q16. stock_ready ໭າຍຄວາມວ່າແນວໃດ?

**A:** ສະຕັອກຖືກ earmark ໃຫ້ການຈອງແລ້ວ. ຍົກເລີກຕ້ອງ release_stock ຄືນສາງ.

### Q17. ImportDetail.save() ເຮັດຫຍັງກັບ stock?

**A:** ສ້າງໃ໭່ qty>0 → ເອີ້ນ receive_stock → ເພີ່ມ Product.stock_qty (+ Inventory batch).

### Q18. ເປັນຫຍັງເງິນໃຊ້ Decimal ບໍ່ໃຊ້ Float?

**A:** Float ມີຂໍ້ຜິດຈຸດທົດສະນິຍົມ (0.1+0.2). ເງິນ/ກີບໃຊ້ Decimal(12,2).

### Q19. ລຶບ Product ທີ່ຂາຍແລ້ວໄດ້ບໍ່?

**A:** ບໍ່ — FK ໃຊ້ PROTECT. ປະຕິບັດຈິງ: ຕັ້ງ is_active=False ແທນລຶບ.

### Q20. Customer.user ເປັນ null ໄດ້ເພາະຫຍັງ?

**A:** ລູກຄ້າ walk-in / POS ອາດບໍ່ມີບັນຊີເວັບ. ລູກຄ້າເວັບທີ່ລົງທະບຽນຈະມີ User + Customer.

### Q21. ເປັນຫຍັງເກັບ slip_url ບໍ່ເກັບຮູບ binary ໃນ DB?

**A:** ເກັບ path/URL; ໄຟລ໌ຢູ່ storage (Supabase / MEDIA). ຮູບໃຫຍ່ໃນ Postgres ຈະເຮັດ DB ໃຫຍ່/ຊ້າ.

### Q22. FIFO ໃນສາງ໭າຍຄວາມວ່າແນວໃດ?

**A:** First In First Out — ຫັກ batch Inventory ເກົ່າກ່ອນ (ຕາມ created_at) ເມື່ອຂາຍ.

### Q23. SQL JOIN ຢູ່ໃສໃນລະບົບນີ້?

**A:** ເມື່ອດຶງ Order ພ້ອມ Customer / OrderItem ໃຊ້ select_related / prefetch_related (ສ້າງ JOIN ໃຫ້).

## 3) System flows

### Q24. ໄຫລການຊື້ເວັບ (ຊື້ດຽວນີ້) ມີຂັ້ນໃດ?

**A:** ເລືອກສິນຄ້າ → ກະຕ່າ → checkout (Order PENDING + OrderItem + Bill) → ໂອນ QR → ອັບສະລິບ (Payment + slip_url) → staff ຍືນຍັນ → COMPLETED + ຕັດ stock.

### Q25. ໄຫລການຈອງ?

**A:** Order RESERVED + Reserved + Bill → ອັບສະລິບມັດຈຳ → staff approve → Reserved PAID → ສິນຄ້າມາ/earmark → ລູກຄ້າມາຮັບ → COMPLETED.

### Q26. ໄຫລນຳເຂົ້າສາງ?

**A:** Supplier → PurchaseOrder + PODetail (ຄຳສັ່ງ, ຍັງບໍ່ເພີ່ມ stock) → Imports + ImportDetail → receive_stock → Product.stock_qty ເພີ່ມ.

### Q27. /admin/ /staff/ /pos/ ແຕກຕ່າງກັນແນວໃດ?

**A:** /admin/ = ຈັດການຂໍ້ມູນຫລັກ (superuser). /staff/ = ງານປະຈຳວັນ: ຍືນຍັນສະລິບ, ສາງ, ຈອງ. /pos/ = ຂາຍໜ້າຮ້ານ. / = ຮ້ານເວັບລູກຄ້າ.

### Q28. Role ຜູ້ໃຊ້ມີຫຍັງ?

**A:** Admin (superuser), Staff (User + Employee), Customer (User + Customer).

## 4) Tech / Deploy

### Q29. Stack ເຕັກໂນໂລຍີຫລັກ?

**A:** Django 4.2 + PostgreSQL + HTML/CSS templates + WhiteNoise + Render + GitHub Pages wake page + django-unfold admin. UI ລາວເປັນຫລັກ (lo/en/th).

### Q30. ເປັນຫຍັງມີໜ້າ wake (GitHub Pages)?

**A:** Render free ຫລັບເມື່ອບໍ່ມີຄົນໃຊ້. ໜ້າ wake ping /healthz/ ໃຫ້ຕື່ນກ່ອນເຂົ້າຮ້ານ.

### Q31. ຄວາມປອດໄພພື້ນຖານທີ່ໃຊ້?

**A:** Django CSRF, password hash, login required ສຳລັບ staff/admin, ບໍ່ commit .env/secret, staff ກວດສະລິບກ່ອນຕັດ stock.

### Q32. MVT ໃນ Django ແມ່ນຫຍັງ?

**A:** Model = DB, View = logic ຮັບ request, Template = HTML.

### Q33. ກະຕ່າເກັບແນວໃດ?

**A:** ເກັບໃນ session ກ່ອນ; ເມື່ອ checkout ຈຶ່ງຂຽນຕາຕະລາງ Order / OrderItem.

## 5) Short answers

### Q34. ອະທິບາຍລະບົບໃນ 20 ວິນາທີ

**A:** Django + PostgreSQL: ຄົນ (User/Employee/Customer) → ຂາຍ (Order/OrderItem/Bill/Payment/Reserved) → ສິນຄ້າ (Product.stock_qty) → ສາງ (Supplier→PO→Import). ເວັບຕັດ stock ຫລັງອະນຸມັດສະລິບ; POS ຕັດທັນທີ.

### Q35. CRUD ແມ່ນຫຍັງ?

**A:** Create, Read, Update, Delete — ເພີ່ມ / ເບິ່ງ / ແກ້ / ລຶບ ຂໍ້ມູນ.

### Q36. Transaction ແມ່ນຫຍັງ?

**A:** ກຸ່ມຄຳສັ່ງ DB ທີ່ສຳເລັດທັງ໭ົດ ຫລື ຍົກເລີກທັງ໭ົດ (atomic). ຕົວຢ່າງ: ສ້າງ Order + OrderItem + Bill ພ້ອມກັນ.

### Q37. ຈຸດເດັ່ນຂອງໂປຣເຈັກນີ້?

**A:** ຄົບທັງຮ້ານອອນໄລນ໌ + POS + staff ຍືນຍັນສະລິບ + ສາງ + ຈອງ; UI ລາວ; ກີບ; deploy ຟຮี.

### Q38. ຂໍ້ຈຳກັດ / ສິ່ງທີ່ຈະພັດທະນາຕໍ່?

**A:** Cold start Render free; ຍັງບໍ່ມີ ProductVariant; ອາດເພີ່ມລາຍງານເລິກ, SMS, ຫລື payment gateway ອັຕໂນມັດ.

> ບອກຂໍ້ຈຳກັດແບບຊື່ສັດ = ອາຈານມັກ

## ວິທີຕອບໃຫ້ປະທັບໃຈ

1. ນິຍາມສັ້ນ → 2. ຕົວຢ່າງຈາກໂປຣເຈັກ → 3. ເຫດຜົນ

ຕົວຢ່າງ: *Foreign Key ຄື… ໃນລະບົບ OrderItem.product ໃຊ້ PROTECT ເພາະບໍ່ຍາກເສຍປະຫວັດການຂາຍ.*

## Demo 2 ນາທີ

wake → ຊື້ເວັບ → ອັບສະລິບ → Staff ຍືນຍັນ → Admin Order/Bill/Payment → ສາງ/ຈອງ

*Total: 38 questions*
