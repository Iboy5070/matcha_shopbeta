from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "name_th", "name_en", "slug")
    search_fields = ("name", "name_th", "name_en", "slug")
    fieldsets = (
        ("ຂໍ້ມູນຫຼັກ", {
            "fields": ("name", "slug"),
            "description": "ໝວດໝູ່ສຳລັບຈັດກຸ່ມສິນຄ້າໃນຮ້ານ",
        }),
        ("ພາສາອື່ນ (ທາງເລືອກ)", {
            "fields": ("name_th", "name_en"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "category", "price", "stock_qty", "is_featured", "active_status")
    list_editable = ("stock_qty", "price")
    search_fields = ("name", "slug", "name_en", "name_th")
    list_filter = ("category", "is_active", "is_featured")
    fieldsets = (
        ("ຂໍ້ມູນສິນຄ້າ", {
            "fields": ("category", "name", "description", "price", "stock_qty"),
            "description": "ຂໍ້ມູນທີ່ລູກຄ້າເຫັນໃນຮ້ານ — ຕື່ມໃຫ້ຄົບເພື່ອຂາຍງ່າຍ",
        }),
        ("ຮູບພາບ", {
            "fields": ("image_url", "image"),
            "description": "ແນະນຳໃຊ້ລິ້ງ URL (ບໍ່ຫາຍເມື່ອ deploy). ຖ້າມີທັງສອງ — ລະບົບໃຊ້ URL ກ່ອນ",
        }),
        ("ການສະແດງຜົນ", {
            "fields": ("is_active", "is_featured", "slug"),
        }),
        ("ພາສາອື່ນ (ທາງເລືອກ)", {
            "fields": ("name_th", "name_en", "description_th", "description_en"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="ເປີດຂາຍ", boolean=True)
    def active_status(self, obj):
        return obj.is_active
