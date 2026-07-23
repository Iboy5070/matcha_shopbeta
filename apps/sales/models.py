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

    order_date = models.DateTimeField("ວັນທີສັ່ງ", auto_now_add=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="ລູກຄ້າ",
        help_text="ອໍເດີຈາກເວັບມັກມີລູກຄ້າ · POS ອາດບໍ່ມີ",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_orders",
        verbose_name="ພະນັກງານ",
        help_text="ຜູ້ຂາຍໜ້າຮ້ານ (POS). ອໍເດີເວັບອາດປ່ອຍວ່າງໄດ້",
    )
    status = models.CharField(
        "ສະຖານະ",
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="ລໍຖ້າ = ຍັງບໍ່ຈ່າຍ · ສຳເລັດ = ຈ່າຍ/ຮັບເຄື່ອງແລ້ວ",
    )

    class Meta:
        verbose_name = "ອໍເດີ"
        verbose_name_plural = "ອໍເດີ"

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="ອໍເດີ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="ສິນຄ້າ")
    quantity = models.PositiveIntegerField("ຈຳນວນ", default=1)
    price = models.DecimalField("ລາຄາ/ຫນ່ວຍ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal = models.DecimalField("ລວມແຖວ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "ລາຍການໃນອໍເດີ"
        verbose_name_plural = "ລາຍການໃນອໍເດີ"

    def __str__(self):
        return f"{self.order} - {self.product.name}"


class Bill(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "ຍັງບໍ່ຊຳລະ"
        PARTIAL = "PARTIAL", "ຊຳລະບາງສ່ວນ"
        PAID = "PAID", "ຊຳລະຄົບ"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="bill", verbose_name="ອໍເດີ")
    bill_date = models.DateTimeField("ວັນທີບິນ", auto_now_add=True)
    total_amount = models.DecimalField("ຍອດທັງໝົດ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_amount = models.DecimalField("ຈ່າຍແລ້ວ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance_due = models.DecimalField("ຄ້າງຊຳລະ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField("ສະຖານະບິນ", max_length=30, choices=Status.choices, default=Status.PENDING)

    class Meta:
        verbose_name = "ບິນ"
        verbose_name_plural = "ບິນ"

    def __str__(self):
        return f"Bill #{self.id} for {self.order}"


class Payment(models.Model):
    class PayWith(models.TextChoices):
        CASH = "CASH", "ເງິນສົດ"
        TRANSFER = "TRANSFER", "ໂອນ"
        QR = "QR", "QR"

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="payments", verbose_name="ບິນ")
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_payments",
        verbose_name="ພະນັກງານຮັບເງິນ",
    )
    pay_amount = models.DecimalField("ຈຳນວນເງິນ (ກີບ)", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pay_with = models.CharField("ວິທີຈ່າຍ", max_length=50, choices=PayWith.choices, default=PayWith.TRANSFER)
    pay_date = models.DateTimeField("ວັນທີຈ່າຍ", auto_now_add=True)
    slip_url = models.CharField(
        "ລິ້ງຮູບສະລິບ",
        max_length=500,
        null=True,
        blank=True,
        help_text="ລິ້ງຮູບໂອນເງິນທີ່ລູກຄ້າອັບໂຫຼດ — ພະນັກງານກວດໃນໜ້າ Staff",
    )

    class Meta:
        verbose_name = "ການຊຳລະເງິນ"
        verbose_name_plural = "ການຊຳລະເງິນ"

    def __str__(self):
        return f"Payment #{self.id} for {self.bill}"


class Reserved(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "ຈອງ"
        PAID = "PAID", "ຊຳລະຄົບ"
        COMPLETED = "COMPLETED", "ສຳເລັດ"
        CANCELLED = "CANCELLED", "ຍົກເລີກ"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservations", verbose_name="ອໍເດີ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="ສິນຄ້າ")
    quantity = models.PositiveIntegerField("ຈຳນວນ", default=1)
    deposit_amount = models.DecimalField(
        "ມັດຈຳ (ກີບ)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="ເງິນທີ່ລູກຄ້າຈ່າຍກ່ອນ (ປົກກະຕິ 50%)",
    )
    remain_amount = models.DecimalField(
        "ຄ້າງຈ່າຍ (ກີບ)",
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="ເງິນທີ່ຕ້ອງຈ່າຍເພີ່ມເມື່ອຮັບສິນຄ້າ",
    )
    status = models.CharField("ສະຖານະຈອງ", max_length=30, choices=Status.choices, default=Status.RESERVED)
    stock_ready = models.BooleanField(
        "ສິນຄ້າພ້ອມແລ້ວ",
        default=False,
        help_text="ຕິກເມື່ອສິນຄ້າມາຮອດ/ຈັດໃຫ້ການຈອງນີ້ແລ້ວ — ລູກຄ້າສາມາດມາຮັບໄດ້",
    )
    res_date = models.DateTimeField("ວັນທີຈອງ", auto_now_add=True)
    expire_at = models.DateTimeField("ໝົດອາຍຸຈອງ", help_text="ຫຼັງວັນນີ້ການຈອງອາດຖືກຍົກເລີກ")

    class Meta:
        verbose_name = "ການຈອງສິນຄ້າ"
        verbose_name_plural = "ການຈອງສິນຄ້າ"

    def __str__(self):
        return f"Reservation #{self.id} for {self.product.name}"
