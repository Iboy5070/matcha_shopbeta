from django.db import models
from django.contrib.auth import get_user_model
from apps.catalog.models import ProductVariant
from apps.sales.models import Order

User = get_user_model()


class StockMovement(models.Model):
    IN = "IN"
    OUT = "OUT"
    ADJUST = "ADJUST"

    TYPE_CHOICES = [
        (IN, "IN"),
        (OUT, "OUT"),
        (ADJUST, "ADJUST"),
    ]

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="stock_movements"
    )
    movement_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    qty = models.IntegerField()

    reason = models.CharField(max_length=200, blank=True)
    ref_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements"
    )

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant.sku} {self.movement_type} {self.qty}"
