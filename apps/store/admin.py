from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import CustomerProfile, PaymentConfirmation, WebOrder, WebOrderItem


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "phone", "created_at")
    search_fields = ("user__username", "user__email", "user__first_name", "phone")
    readonly_fields = ("created_at",)

    @admin.display(description="ຊື່")
    def display_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description="ອີເມວ")
    def email(self, obj):
        return obj.user.email


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
                    "ສະຖານະ: NEW → WAITING_PAYMENT → PAYMENT_REVIEW → PAID → SHIPPING → DONE. "
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

    @admin.action(description="ຢືນຢັນຊຳລະ → PAID")
    def mark_paid(self, request, queryset):
        updated = queryset.update(status="PAID")
        self.message_user(request, f"ປ່ຽນ {updated} ອໍເດີເປັນ PAID")

    actions = [mark_paid]


@admin.register(PaymentConfirmation)
class PaymentConfirmationAdmin(admin.ModelAdmin):
    list_display = ("order", "paid_amount_display", "bank_name", "slip_thumb", "created_at")
    list_filter = ("created_at",)
    search_fields = ("order__order_no",)
    readonly_fields = ("created_at", "slip_preview")
    ordering = ("-created_at",)
    fieldsets = (
        (
            "ຢືນຢັນການໂອນ",
            {
                "fields": ("order", "paid_amount", "bank_name", "slip_image", "slip_preview", "note", "created_at"),
                "description": "ລູກຄ້າອັບໂຫຼດສลິບຈາກໜ້າເວັບ — ກວດແລ້ວປ່ຽນສະຖານະອໍເດີເປັນ PAID.",
            },
        ),
    )

    @admin.display(description="ຈຳນວນ")
    def paid_amount_display(self, obj):
        return f"{int(obj.paid_amount):,} ກີບ"

    @admin.display(description="ສลິບ")
    def slip_thumb(self, obj):
        url = obj.display_slip_url
        if not url:
            return "—"
        if not url.startswith("http"):
            url = settings.SITE_URL.rstrip("/") + url
        return format_html(
            '<a href="{}" target="_blank"><img src="{}" width="40" height="40" style="object-fit:cover;border-radius:4px"></a>',
            url,
            url,
        )

    @admin.display(description="ສลິບ (ໃຫຍ່)")
    def slip_preview(self, obj):
        url = obj.display_slip_url
        if not url:
            return "—"
        if not url.startswith("http"):
            url = settings.SITE_URL.rstrip("/") + url
        return format_html(
            '<a href="{}" target="_blank"><img src="{}" style="max-width:320px;max-height:400px;border-radius:8px;border:1px solid #ddd"></a>',
            url,
            url,
        )

    @admin.action(description="ຢືນຢັນຊຳລະອໍເດີ → PAID")
    def mark_orders_paid(self, request, queryset):
        order_ids = queryset.values_list("order_id", flat=True).distinct()
        updated = WebOrder.objects.filter(id__in=order_ids).update(status="PAID")
        self.message_user(request, f"ປ່ຽນ {updated} ອໍເດີເປັນ PAID")

    actions = [mark_orders_paid]
