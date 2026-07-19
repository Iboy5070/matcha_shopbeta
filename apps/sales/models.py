from decimal import Decimal
from django.db import models
from apps.store.models import Customer, Employee
from apps.catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ລໍຖ້າ"
        RESERVED = "RESERVED", "ຈອງ"
        COMPLETED = "COMPLETED", "ສຳເລັດ"
        CANCELLED = "CANCELLED", "ຍົກເລີກ"

    order_date = models.DateTimeField("Order_date", auto_now_add=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Cus_ID",
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="processed_orders", verbose_name="Emp_ID",
        help_text="nullable ສຳລັບ web order (ບົດ: NOT NULL)",
    )
    status = models.CharField("Status", max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ອໍເດີ (Orders)"
        verbose_name_plural = "ອໍເດີ (Orders)"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Order_ID")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Pro_ID")
    quantity = models.PositiveIntegerField("Quantity", default=1)
    price = models.DecimalField("Price", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ລາຍລະອຽດ (Order_detail)"
        verbose_name_plural = "ລາຍລະອຽດ (Order_detail)"

    def __str__(self):
        return f"{self.order} - {self.product.name}"


class Bill(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ຍັງບໍ່ຊຳລະ"
        PARTIAL = "PARTIAL", "ຊຳລະບາງສ່ວນ"
        PAID = "PAID", "ຊຳລະຄົບ"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="bill", verbose_name="Order_ID")
    bill_date = models.DateTimeField("Bill_date", auto_now_add=True)
    total_amount = models.DecimalField("Total_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField("Paid_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField("Balance_due", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("Status", max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ບິນ (Bill)"
        verbose_name_plural = "ບິນ (Bills)"

    def __str__(self):
        return f"Bill #{self.id} for {self.order}"


class Payment(models.Model):
    class PayWith(models.TextChoices):
        CASH = "CASH", "ເງິນສົດ"
        TRANSFER = "TRANSFER", "ໂອນ"
        QR = "QR", "QR"

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="payments", verbose_name="Bill_ID")
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="processed_payments", verbose_name="Emp_ID",
    )
    pay_amount = models.DecimalField("Pay_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pay_with = models.CharField("Pay_with", max_length=50, choices=PayWith.choices, default=PayWith.TRANSFER)
    pay_date = models.DateTimeField("Pay_date", auto_now_add=True)
    slip_url = models.CharField(
        "Img_path (Slip URL)",
        max_length=500,
        null=True,
        blank=True,
        help_text="ບົດ: Img_path — URL ຮູບ slip ຈາກ Supabase",
    )

    class Meta:
        verbose_name = "ການຊຳລະເງິນ (Payment)"
        verbose_name_plural = "ການຊຳລະເງິນ (Payments)"

    def __str__(self):
        return f"Payment #{self.id} for {self.bill}"


class Reserved(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "ຈອງ"
        PAID = "PAID", "ຊຳລະຄົບ"
        COMPLETED = "COMPLETED", "ສຳເລັດ"
        CANCELLED = "CANCELLED", "ຍົກເລີກ"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservations", verbose_name="Order_ID")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Pro_ID")
    quantity = models.PositiveIntegerField("Quantity", default=1)
    deposit_amount = models.DecimalField("Deposit_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remain_amount = models.DecimalField("Remain_amount", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("Status", max_length=30, choices=Status.choices, default=Status.RESERVED)
    stock_ready = models.BooleanField(
        "Stock_ready (impl.)",
        default=False,
        help_text="ເພີ່ມຕອນ implement — ສິນຄ້າຈັດໃຫ້ຈອງແລ້ວ (ບົດບໍ່ມີ)",
    )
    res_date = models.DateTimeField("Res_date", auto_now_add=True)
    expire_at = models.DateTimeField("Expire_at")

    class Meta:
        verbose_name = "ສິນຄ້າຈອງ (Reserved)"
        verbose_name_plural = "ສິນຄ້າຈອງ (Reserved)"

    def __str__(self):
        return f"Reservation #{self.id} for {self.product.name}"
