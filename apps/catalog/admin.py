from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "category", "price", "active_status")
    search_fields = ("name", "slug")
    list_filter = ("category", "is_active")

    @admin.display(description="Active")
    def active_status(self, obj):
        return "✅" if obj.is_active else "❌"
