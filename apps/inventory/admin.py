from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Supplier, PurchaseOrder, PODetail, Imports, ImportDetail, Inventory

@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("sup_name", "sup_tel", "email")

class PODetailInline(TabularInline):
    model = PODetail
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ModelAdmin):
    list_display = ("id", "supplier", "employee", "po_date", "total_amount", "status")
    inlines = [PODetailInline]

class ImportDetailInline(TabularInline):
    model = ImportDetail
    extra = 1

@admin.register(Imports)
class ImportsAdmin(ModelAdmin):
    list_display = ("id", "purchase_order", "supplier", "employee", "imp_date", "total_amount")
    inlines = [ImportDetailInline]

@admin.register(Inventory)
class InventoryAdmin(ModelAdmin):
    list_display = ("product", "quantity", "expiry_date", "created_at")

