from decimal import Decimal
from django.db import models
from apps.store.models import Employee
from apps.catalog.models import Product


class Supplier(models.Model):
    sup_name = models.CharField("ຊື່ຜູ້ສະໜອງ", max_length=100)
    sup_tel = models.CharField("ເບີໂທ", max_length=20)
    sup_address = models.TextField("ທີ່ຢູ່")
    email = models.EmailField("ອີເມວ", blank=True)

    class Meta:
        verbose_name = "ຜູ້ສະໜອງ"
        verbose_name_plural = "ຜູ້ສະໜອງ"

    def __str__(self):
        return self.sup_name


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ລໍຖ້າ"
        COMPLETED = "COMPLETED", "ສຳເລັດ"
        CANCELLED = "CANCELLED", "ຍົກເລີກ"

    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ພະນັກງານສັ່ງຊື້"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="ຜູ້ສະໜອງ")
    po_date = models.DateTimeField("ວັນທີສັ່ງຊື້", auto_now_add=True)
    total_amount = models.DecimalField("ຍອດລວມ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("ສະຖານະ", max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ໃບສັ່ງຊື້"
        verbose_name_plural = "ໃບສັ່ງຊື້"

    def __str__(self):
        return f"PO #{self.id} from {self.supplier.sup_name}"


class PODetail(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="details", verbose_name="ໃບສັ່ງຊື້"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="ສິນຄ້າ")
    quantity = models.PositiveIntegerField("ຈຳນວນ", default=1)
    cost_price = models.DecimalField("ຕົ້ນທຶນ/ຫນ່ວຍ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("ລວມແຖວ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ລາຍການໃບສັ່ງຊື້"
        verbose_name_plural = "ລາຍການໃບສັ່ງຊື້"

    def __str__(self):
        return f"PO Detail #{self.id}"


class Imports(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="ໃບສັ່ງຊື້")
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ພະນັກງານຮັບເຂົ້າ"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="ຜູ້ສະໜອງ")
    imp_date = models.DateTimeField("ວັນທີນຳເຂົ້າ", auto_now_add=True)
    total_amount = models.DecimalField("ຍອດລວມ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ນຳເຂົ້າສິນຄ້າ"
        verbose_name_plural = "ນຳເຂົ້າສິນຄ້າ"

    def __str__(self):
        return f"Import #{self.id} for PO #{self.purchase_order_id}"


class ImportDetail(models.Model):
    imports = models.ForeignKey(Imports, on_delete=models.CASCADE, related_name="details", verbose_name="ໃບນຳເຂົ້າ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="ສິນຄ້າ")
    quantity = models.PositiveIntegerField(
        "ຈຳນວນ",
        default=1,
        help_text="ເມື່ອບັນທຶກ — ລະບົບເພີ່ມສະຕັອກອັດຕະໂນມັດ",
    )
    cost_price = models.DecimalField("ຕົ້ນທຶນ/ຫນ່ວຍ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("ລວມແຖວ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField("ວັນທີບັນທຶກ", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "ລາຍການນຳເຂົ້າ"
        verbose_name_plural = "ລາຍການນຳເຂົ້າ"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.quantity > 0:
            from apps.catalog.stock import receive_stock
            receive_stock(self.product_id, self.quantity)

    def __str__(self):
        return f"Import Detail #{self.id}"


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory", verbose_name="ສິນຄ້າ")
    quantity = models.IntegerField(
        "ຈຳນວນໃນຊຸດນີ້",
        default=0,
        help_text="ເພີ່ມ batch ໃໝ່ — ລະບົບຈະອັບເດດຈຳນວນຂາຍລວມໃຫ້",
    )
    expiry_date = models.DateField("ວັນໝົດອາຍຸ", null=True, blank=True, help_text="ປ່ອຍວ່າງໄດ້ຖ້າບໍ່ມີວັນໝົດອາຍຸ")
    created_at = models.DateTimeField("ວັນທີເພີ່ມ", auto_now_add=True)

    class Meta:
        verbose_name = "ສະຕັອກໃນສາງ"
        verbose_name_plural = "ສະຕັອກໃນສາງ"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.quantity > 0:
            from apps.catalog.stock import receive_stock
            receive_stock(self.product_id, self.quantity)

    def __str__(self):
        return f"Inventory for {self.product.name}"
