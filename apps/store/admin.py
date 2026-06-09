from django.contrib import admin

from .models import PaymentConfirmation, WebOrder, WebOrderItem


class WebOrderItemInline(admin.TabularInline):
    model = WebOrderItem
    extra = 0
    readonly_fields = ("variant", "qty", "unit_price", "line_total")


@admin.register(WebOrder)
class WebOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_no",
        "customer_name",
        "phone",
        "grand_total",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_no", "customer_name", "phone")
    readonly_fields = ("order_no", "created_at")
    inlines = [WebOrderItemInline]


@admin.register(PaymentConfirmation)
class PaymentConfirmationAdmin(admin.ModelAdmin):
    list_display = ("order", "paid_amount", "bank_name", "created_at")
    search_fields = ("order__order_no",)
    readonly_fields = ("created_at",)
