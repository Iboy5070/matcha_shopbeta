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
            defaults={"name": "ຜົງມັດຊາ"},
        )

        product = Product.objects.filter(
            Q(name__icontains="Ceremonial") | Q(slug__icontains="ceremonial")
        ).first()

        if product:
            product.image_url = CEREMONIAL_IMAGE
            product.is_featured = True
            product.is_active = True
            product.save(update_fields=["image_url", "is_featured", "is_active"])
        else:
            product, _ = Product.objects.get_or_create(
                slug="ceremonial-matcha",
                defaults={
                    "category": cat,
                    "name": "ມັດຊາ ເກຣດ Ceremonial",
                    "description": "ມັດຊາເກຣດ Ceremonial organic — 30g",
                    "image_url": CEREMONIAL_IMAGE,
                    "is_featured": True,
                    "is_active": True,
                },
            )
            if not product.image_url:
                product.image_url = CEREMONIAL_IMAGE
                product.save(update_fields=["image_url"])

        ProductVariant.objects.get_or_create(
            sku="MATCHA-CER-30",
            defaults={
                "product": product,
                "display_name": "30 ກຣາມ",
                "weight_g": 30,
                "price": Decimal("49000.00"),
                "sell_price": Decimal("49000.00"),
                "stock_qty": 100,
                "is_active": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Catalog ready (Ceremonial image synced)."))
