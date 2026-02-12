from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("variant", "movement_type", "qty", "actor", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("variant__sku", "variant__product__name")
