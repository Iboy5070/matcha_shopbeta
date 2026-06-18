from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductVariant


class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "sku",
        "display_name",
        "sell_price",
        "stock_qty",
        "is_active",
    )
    verbose_name = "ຕົວເລືອກສິນຄ້າ (Variant)"
    verbose_name_plural = "ຕົວເລືອກສິນຄ້າ — ລາຄາ, SKU, ສຕັອກ"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "category", "price_range", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "slug", "variants__sku")
    list_editable = ("is_featured", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VariantInline]
    fieldsets = (
        (
            "ຂໍ້ມູນຫຼັກ",
            {
                "fields": ("category", "name", "slug", "description"),
                "description": (
                    "ຊື່ສິນຄ້າ + ຄຳອະທິບາຍ — ສະແດງໃນໜ້າຮ້ານ. "
                    "Slug ສ້າງອັດຕະໂນມັດຈາກຊື່."
                ),
            },
        ),
        (
            "ຮູບສິນຄ້າ",
            {
                "fields": ("image_url", "image"),
                "description": (
                    "① Image URL = ລິ້ງ CDN (ແນະນຳ production). "
                    "② Image = ອັບໂຫຼດໄຟລ໌ (dev). "
                    "ຢ່າງໃດຢ່າງໜຶ່ງຕ້ອງມີ."
                ),
            },
        ),
        (
            "ການສະແດງ",
            {
                "fields": ("is_featured", "is_active"),
                "description": (
                    "Featured = ໜ້າຫຼັກ. Active = ເປີດຂາຍ."
                ),
            },
        ),
    )

    @admin.display(description="ຮູບ")
    def thumb(self, obj):
        url = obj.display_image
        if url:
            return format_html(
                '<img src="{}" width="48" height="48" style="object-fit:cover;border-radius:6px">',
                url,
            )
        return "—"

    @admin.display(description="ລາຄາ (ກີບ)")
    def price_range(self, obj):
        prices = [
            v.sell_price or v.price
            for v in obj.variants.filter(is_active=True)
        ]
        if not prices:
            return "—"
        lo, hi = min(prices), max(prices)
        if lo == hi:
            return f"{int(lo):,}"
        return f"{int(lo):,} – {int(hi):,}"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    search_fields = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": ("name", "slug"),
                "description": "ຫມວດສິນຄ້າ — ເຊັ່ນ ຜົງมัชะ, อุปกรณ์",
            },
        ),
    )

    @admin.display(description="ຈຳນວນສິນຄ້າ")
    def product_count(self, obj):
        return obj.products.count()

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            base = slugify(obj.name) or f"cat-{abs(hash(obj.name)) % 99999}"
            slug, n = base, 1
            while Category.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            obj.slug = slug
        super().save_model(request, obj, form, change)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("display_name", "product", "sku", "sell_price", "stock_qty", "is_active")
    list_filter = ("is_active", "product__category")
    search_fields = ("sku", "display_name", "product__name")
    list_editable = ("sell_price", "stock_qty", "is_active")
    fieldsets = (
        (
            None,
            {
                "fields": ("product", "sku", "display_name", "sell_price", "price", "stock_qty", "is_active"),
                "description": (
                    "Variant = ສິນຄ້າທີ່ຂາຍຈິງ (ເຊັ່ນ 30g, 50g). "
                    "Sell price = ລາຄາຂາຍ. Stock = ຈຳນວນເຫຼືອ."
                ),
            },
        ),
    )
