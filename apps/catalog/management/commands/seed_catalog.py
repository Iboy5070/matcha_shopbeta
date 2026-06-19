from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.catalog.models import Category, Product, ProductVariant

CEREMONIAL_IMAGE = (
    "https://getcrafti.co/cdn/shop/files/Ceremonialmatcha30gnobg.png?v=1737512532"
)


class Command(BaseCommand):
    help = "Seed catalog + sync CDN image URLs (idempotent)"

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(
            slug="matcha-powder",
            defaults={
                "name": "ຜົງມັດຊາ",
                "name_th": "ผงมัทฉะ",
                "name_en": "Matcha powder",
            },
        )
        if not cat.name_th:
            cat.name_th = "ผงมัทฉะ"
            cat.name_en = "Matcha powder"
            cat.save(update_fields=["name_th", "name_en"])

        product = Product.objects.filter(
            Q(name__icontains="Ceremonial") | Q(slug__icontains="ceremonial")
        ).first()

        if product:
            product.image_url = CEREMONIAL_IMAGE
            product.is_featured = True
            product.is_active = True
            product.name_th = product.name_th or "มัทฉะเกรด Ceremonial"
            product.name_en = product.name_en or "Ceremonial Grade Matcha"
            product.description_th = product.description_th or "มัทฉะเกรด Ceremonial organic — 30g"
            product.description_en = product.description_en or "Organic ceremonial grade matcha — 30g"
            product.save(
                update_fields=[
                    "image_url",
                    "is_featured",
                    "is_active",
                    "name_th",
                    "name_en",
                    "description_th",
                    "description_en",
                ]
            )
        else:
            product, _ = Product.objects.get_or_create(
                slug="ceremonial-matcha",
                defaults={
                    "category": cat,
                    "name": "ມັດຊາ ເກຣດ Ceremonial",
                    "name_th": "มัทฉะเกรด Ceremonial",
                    "name_en": "Ceremonial Grade Matcha",
                    "description": "ມັດຊາເກຣດ Ceremonial organic — 30g",
                    "description_th": "มัทฉะเกรด Ceremonial organic — 30g",
                    "description_en": "Organic ceremonial grade matcha — 30g",
                    "image_url": CEREMONIAL_IMAGE,
                    "is_featured": True,
                    "is_active": True,
                },
            )
            if not product.image_url:
                product.image_url = CEREMONIAL_IMAGE
                product.save(update_fields=["image_url"])

        variant, _ = ProductVariant.objects.get_or_create(
            sku="MATCHA-CER-30",
            defaults={
                "product": product,
                "display_name": "30 ກຣາມ",
                "display_name_th": "30 กรัม",
                "display_name_en": "30 g",
                "weight_g": 30,
                "price": Decimal("49000.00"),
                "sell_price": Decimal("49000.00"),
                "stock_qty": 100,
                "is_active": True,
            },
        )
        if not variant.display_name_th:
            variant.display_name_th = "30 กรัม"
            variant.display_name_en = "30 g"
            variant.save(update_fields=["display_name_th", "display_name_en"])

        self.stdout.write(self.style.SUCCESS("Catalog ready (Ceremonial image synced)."))
