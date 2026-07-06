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

    order_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_orders")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ອໍເດີ (Order)"
        verbose_name_plural = "ອໍເດີ (Orders)"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ລາຍການອໍເດີ (Order Item)"
        verbose_name_plural = "ລາຍການອໍເດີ (Order Items)"

    def __str__(self):
        return f"{self.order} - {self.product.name}"


class Bill(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ຍັງບໍ່ຊຳລະ"
        PARTIAL = "PARTIAL", "ຊຳລະບາງສ່ວນ"
        PAID = "PAID", "ຊຳລະຄົບ"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="bill")
    bill_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)

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

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="payments")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_payments")
    pay_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pay_with = models.CharField(max_length=50, choices=PayWith.choices, default=PayWith.TRANSFER)
    pay_date = models.DateTimeField(auto_now_add=True)
    slip_url = models.CharField(max_length=500, null=True, blank=True)

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

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservations")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remain_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.RESERVED)
    stock_ready = models.BooleanField(
        "ສິນຄ້າພ້ອມ (Stock ready)",
        default=False,
        help_text="ອັດຕະໂນມັດ True ເມື່ອສິນຄ້າໃໝ່ເຂົ້າ ແລະ ຈັດສັນໃຫ້ການຈອງນີ້ແລ້ວ",
    )
    res_date = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField()

    class Meta:
        verbose_name = "ສິນຄ້າຈອງ (Reserved)"
        verbose_name_plural = "ສິນຄ້າຈອງ (Reserved)"

    def __str__(self):
        return f"Reservation #{self.id} for {self.product.name}"
