from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from .models import Order, OrderItem, Bill, Payment, Reserved


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    verbose_name = "ລາຍການສິນຄ້າ"
    verbose_name_plural = "ລາຍການສິນຄ້າໃນອໍເດີ"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "order_date", "customer", "employee", "status")
    search_fields = ("customer__cus_name", "employee__emp_name", "id")
    list_filter = ("status",)
    inlines = [OrderItemInline]
    fieldsets = (
        ("ອໍເດີ", {
            "fields": ("customer", "employee", "status"),
            "description": "ອໍເດີເວັບ = ມີລູກຄ້າ · ອໍເດີ POS = ມີພະນັກງານ",
        }),
    )


@admin.register(Bill)
class BillAdmin(ModelAdmin):
    list_display = ("id", "order", "bill_date", "total_amount", "paid_amount", "balance_due", "status")
    list_filter = ("status",)
    fieldsets = (
        ("ບິນ", {
            "fields": ("order", "total_amount", "paid_amount", "balance_due", "status"),
            "description": "ຍອດເງິນຂອງອໍເດີ — ພະນັກງານກວດສະລິບໃນໜ້າ Staff",
        }),
    )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("id", "bill", "pay_amount", "pay_with", "pay_date", "slip_preview")
    list_filter = ("pay_with",)
    fieldsets = (
        ("ການຊຳລະ", {
            "fields": ("bill", "employee", "pay_amount", "pay_with", "slip_url"),
            "description": "ຖ້າມີລິ້ງສະລິບ — ໄປກວດທີ່ Staff → ກວດສະລິບ",
        }),
    )

    @admin.display(description="ສະລິບ")
    def slip_preview(self, obj):
        if obj.slip_url:
            return format_html('<a href="{}" target="_blank" rel="noopener">ເບິ່ງຮູບ</a>', obj.slip_url)
        return "—"


@admin.register(Reserved)
class ReservedAdmin(ModelAdmin):
    list_display = ("id", "product", "quantity", "deposit_amount", "remain_amount", "stock_ready", "status", "expire_at")
    list_filter = ("status", "stock_ready")
    fieldsets = (
        ("ການຈອງ", {
            "fields": ("order", "product", "quantity", "deposit_amount", "remain_amount", "status", "stock_ready", "expire_at"),
            "description": "ຈອງ = ຈ່າຍມັດຈຳກ່ອນ · ຕິກ 'ສິນຄ້າພ້ອມ' ເມື່ອຈັດສິນຄ້າໃຫ້ແລ້ວ",
        }),
    )
