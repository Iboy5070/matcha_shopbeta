from decimal import Decimal
from django.db import models
from apps.store.models import Employee
from apps.catalog.models import Product

class Supplier(models.Model):
    sup_name = models.CharField("Sup_Name", max_length=100)
    sup_tel = models.CharField("Sup_Tel", max_length=20)
    sup_address = models.TextField("Sup_Address")
    email = models.EmailField("Email")

    class Meta:
        verbose_name = "ຜູ້ສະໜອງ (Supplier)"
        verbose_name_plural = "ຜູ້ສະໜອງ (Suppliers)"

    def __str__(self):
        return self.sup_name

class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ລໍຖ້າ"
        COMPLETED = "COMPLETED", "ສຳເລັດ"
        CANCELLED = "CANCELLED", "ຍົກເລີກ"

    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Emp_ID")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Sup_ID")
    po_date = models.DateTimeField("PO_date", auto_now_add=True)
    total_amount = models.DecimalField("Total_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("Status", max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ໃບສັ່ງຊື້ (Purchase_order)"
        verbose_name_plural = "ໃບສັ່ງຊື້ (Purchase_order)"

    def __str__(self):
        return f"PO #{self.id} from {self.supplier.sup_name}"

class PODetail(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="details", verbose_name="PO_ID")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Pro_ID")
    quantity = models.PositiveIntegerField("Quantity", default=1)
    cost_price = models.DecimalField("Cost_price", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ລາຍລະອຽດ PO (PO_detail)"
        verbose_name_plural = "ລາຍລະອຽດ PO (PO_detail)"

    def __str__(self):
        return f"PO Detail #{self.id}"

class Imports(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name="PO_ID")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Emp_ID")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Sup_ID")
    imp_date = models.DateTimeField("Imp_date", auto_now_add=True)
    total_amount = models.DecimalField("Total_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ນຳເຂົ້າ (Import)"
        verbose_name_plural = "ນຳເຂົ້າ (Imports)"

    def __str__(self):
        return f"Import #{self.id} for PO #{self.purchase_order_id}"

class ImportDetail(models.Model):
    imports = models.ForeignKey(Imports, on_delete=models.CASCADE, related_name="details", verbose_name="Imp_ID")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Pro_ID")
    quantity = models.PositiveIntegerField("Quantity", default=1)
    cost_price = models.DecimalField("Cost_price", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField("Created_at", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "ລາຍລະອຽດນຳເຂົ້າ (Import_detail)"
        verbose_name_plural = "ລາຍລະອຽດນຳເຂົ້າ (Import_detail)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.quantity > 0:
            from apps.catalog.stock import receive_stock
            receive_stock(self.product_id, self.quantity)

    def __str__(self):
        return f"Import Detail #{self.id}"

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory", verbose_name="Pro_ID")
    quantity = models.IntegerField("Quantity", default=0)
    expiry_date = models.DateField("Expiry_date", null=True, blank=True)
    created_at = models.DateTimeField("Created_at", auto_now_add=True)

    class Meta:
        verbose_name = "ສິນຄ້າໃນສາງ (Inventory)"
        verbose_name_plural = "ສິນຄ້າໃນສາງ (Inventory)"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.quantity > 0:
            from apps.catalog.stock import receive_stock
            receive_stock(self.product_id, self.quantity)

    def __str__(self):
        return f"Inventory for {self.product.name}"
