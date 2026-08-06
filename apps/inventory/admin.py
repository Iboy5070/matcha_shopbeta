from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, TabularInline
from unfold.widgets import UnfoldAdminTextInputWidget
from .models import Supplier, PurchaseOrder, PODetail, Imports, ImportDetail, Inventory


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("sup_name", "sup_tel", "email")
    search_fields = ("sup_name", "sup_tel", "email")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.TextField) and db_field.name == "sup_address":
            kwargs["widget"] = UnfoldAdminTextInputWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    fieldsets = (
        ("ຜູ້ສະໜອງ", {
            "fields": ("sup_name", "sup_tel", "email", "sup_address"),
            "description": "ບໍລິສັດ/ຄົນທີ່ສົ່ງສິນຄ້າເຂົ້າຮ້ານ",
        }),
    )


class PODetailInline(TabularInline):
    model = PODetail
    extra = 1
    verbose_name_plural = "ລາຍການສິນຄ້າທີ່ສັ່ງ"


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ModelAdmin):
    list_display = ("id", "supplier", "employee", "po_date", "total_amount", "status")
    list_filter = ("status",)
    inlines = [PODetailInline]
    fieldsets = (
        ("ໃບສັ່ງຊື້", {
            "fields": ("supplier", "employee", "total_amount", "status"),
            "description": "ບັນທຶກການສັ່ງຊື້ຈາກຜູ້ສະໜອງ ກ່ອນນຳເຂົ້າສາງ",
        }),
    )


class ImportDetailInline(TabularInline):
    model = ImportDetail
    extra = 1
    verbose_name_plural = "ລາຍການສິນຄ້າທີ່ຮັບເຂົ້າ"


@admin.register(Imports)
class ImportsAdmin(ModelAdmin):
    list_display = ("id", "purchase_order", "supplier", "employee", "imp_date", "total_amount")
    inlines = [ImportDetailInline]
    fieldsets = (
        ("ນຳເຂົ້າສິນຄ້າ", {
            "fields": ("purchase_order", "supplier", "employee", "total_amount"),
            "description": "ເມື່ອເພີ່ມລາຍການນຳເຂົ້າ — ສະຕັອກຈະເພີ່ມອັດຕະໂນມັດ",
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(ModelAdmin):
    list_display = ("product", "quantity", "expiry_date", "created_at")
    list_filter = ("expiry_date",)
    search_fields = ("product__name",)
    fieldsets = (
        ("ສະຕັອກໃນສາງ", {
            "fields": ("product", "quantity", "expiry_date"),
            "description": "ເພີ່ມ batch ສິນຄ້າເຂົ້າສາງ — ຈຳນວນຂາຍລວມຈະອັບເດດໃຫ້",
        }),
    )
