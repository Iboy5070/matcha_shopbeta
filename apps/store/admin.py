from django.contrib import admin
from django.utils.html import format_html

from .models import PaymentConfirmation, WebOrder, WebOrderItem


class WebOrderItemInline(admin.TabularInline):
    model = WebOrderItem
    extra = 0
    readonly_fields = ("variant", "qty", "unit_price", "line_total")
    can_delete = False


@admin.register(WebOrder)
class WebOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_no",
        "customer_name",
        "phone",
        "grand_total_display",
        "status",
        "payment_method",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("order_no", "customer_name", "phone")
    readonly_fields = ("order_no", "created_at", "subtotal", "discount", "grand_total")
    inlines = [WebOrderItemInline]
    ordering = ("-created_at",)
    list_editable = ("status",)
    fieldsets = (
        (
            "ອໍເດີ",
            {
                "fields": ("order_no", "status", "payment_method", "created_at"),
                "description": (
                    "ສະຖານະ: NEW → WAITING_PAYMENT → PAID → SHIPPING → DONE. "
                    "ປ່ຽນເປັນ PAID ເມື່ອກວດສลິບແລ້ວ."
                ),
            },
        ),
        (
            "ລູກຄ້າ",
            {"fields": ("customer_name", "phone", "address")},
        ),
        (
            "ຍອດເງິນ",
            {"fields": ("subtotal", "discount", "grand_total")},
        ),
    )

    @admin.display(description="ຍອດ (ກີບ)")
    def grand_total_display(self, obj):
        return f"{int(obj.grand_total):,}"


@admin.register(PaymentConfirmation)
class PaymentConfirmationAdmin(admin.ModelAdmin):
    list_display = ("order", "paid_amount_display", "bank_name", "slip_thumb", "created_at")
    list_filter = ("created_at",)
    search_fields = ("order__order_no",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    fieldsets = (
        (
            "ຢືນຢັນການໂອນ",
            {
                "fields": ("order", "paid_amount", "bank_name", "slip_image", "note", "created_at"),
                "description": "ລູກຄ້າອັບໂຫຼດສลິບຈາກໜ້າເວັບ — ກວດແລ້ວປ່ຽນສະຖານະອໍເດີເປັນ PAID.",
            },
        ),
    )

    @admin.display(description="ຈຳນວນ")
    def paid_amount_display(self, obj):
        return f"{int(obj.paid_amount):,} ກີບ"

    @admin.display(description="ສลິບ")
    def slip_thumb(self, obj):
        if obj.slip_image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="40" height="40" style="object-fit:cover;border-radius:4px"></a>',
                obj.slip_image.url,
                obj.slip_image.url,
            )
        return "—"
