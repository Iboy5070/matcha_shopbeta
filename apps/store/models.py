from django.db import models
from django.utils import timezone
from apps.catalog.models import ProductVariant


class WebOrder(models.Model):
    STATUS_CHOICES = [
        ("NEW", "NEW"),
        ("WAITING_PAYMENT", "WAITING_PAYMENT"),
        ("PAID", "PAID"),
        ("SHIPPING", "SHIPPING"),
        ("DONE", "DONE"),
        ("CANCEL", "CANCEL"),
    ]

    PAYMENT_CHOICES = [
        ("transfer", "Transfer"),
        ("cod", "Cash on Delivery"),
    ]

    order_no = models.CharField(max_length=30, unique=True)
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="transfer")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="NEW")

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_no


class WebOrderItem(models.Model):
    order = models.ForeignKey(WebOrder, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)

    qty = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.order.order_no} - {self.variant.sku}"


class PaymentConfirmation(models.Model):
    order = models.ForeignKey(WebOrder, on_delete=models.CASCADE, related_name="payment_confirmations")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_at = models.DateTimeField(default=timezone.now)
    bank_name = models.CharField(max_length=120, blank=True)
    note = models.CharField(max_length=255, blank=True)

    slip_image = models.ImageField(upload_to="slips/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Confirm {self.order.order_no}"
