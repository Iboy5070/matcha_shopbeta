from django.contrib import admin
from .models import Category, Product, ProductVariant


class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VariantInline]
    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "description", "is_featured", "is_active")}),
        (
            "ຮູບສິນຄ້າ",
            {
                "fields": ("image_url", "image"),
                "description": (
                    "ໃຊ້ Image URL ສຳລັບລິ້ງ CDN (ຄົງຖາວັນໃນ production). "
                    "ຫຼືອັບໂຫຼດໄຟລ໌ໃນ Image (ໃຊ້ໄດ້ໃນ local dev)."
                ),
            },
        ),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            base = slugify(obj.name) or f"cat-{abs(hash(obj.name)) % 99999}"
            slug, n = base, 1
            from apps.catalog.models import Category as Cat
            while Cat.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            obj.slug = slug
        super().save_model(request, obj, form, change)

admin.site.register(ProductVariant)
