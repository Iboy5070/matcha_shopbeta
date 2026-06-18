from django.contrib import admin

from .models import ContactMessage, FAQItem, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("company_name", "quote_preview", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("company_name", "quote_th")
    fieldsets = (
        (
            "ຄຳເຫັນຈາກລູກຄ້າ / Partner",
            {
                "fields": ("company_name", "quote_th", "quote_en", "sort_order", "is_active"),
                "description": (
                    "ສະແດງໃນໜ້າຫຼັກ. Sort order = ເລກຍ້ອນ (0 ຂຶ້ນກ່ອນ). "
                    "Quote TH = ພາສາລາວ (ໃຊ້ field ນີ້ເຖິງເລືອກພາສາລາວ)."
                ),
            },
        ),
    )

    @admin.display(description="ຄຳເຫັນ")
    def quote_preview(self, obj):
        return (obj.quote_th[:60] + "…") if len(obj.quote_th) > 60 else obj.quote_th


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question_preview", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("question_lo", "question_th", "answer_lo", "answer_th")
    fieldsets = (
        (
            "ຄຳຖາມ-ຄຳຕອບ (FAQ)",
            {
                "fields": (
                    "question_lo",
                    "answer_lo",
                    "question_th",
                    "answer_th",
                    "question_en",
                    "answer_en",
                    "sort_order",
                    "is_active",
                ),
                "description": (
                    "ລາວ = ເມື່ອເລືອກພາສາລາວ · ไทย = ເມື່ອເລືອກ TH · EN = English. "
                    "Active = ເປີດສະແດງ."
                ),
            },
        ),
    )

    @admin.display(description="ຄຳຖາມ")
    def question_preview(self, obj):
        return (obj.question_lo or obj.question_th)[:70]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "message_preview", "created_at")
    readonly_fields = ("name", "email", "phone", "message", "created_at")
    list_filter = ("created_at",)

    @admin.display(description="ຂໍ້ຄວາມ")
    def message_preview(self, obj):
        return (obj.message[:50] + "…") if len(obj.message) > 50 else obj.message

    def has_add_permission(self, request):
        return False
