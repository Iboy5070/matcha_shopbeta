"""Set product image_url to bundled static files (for Render/demo)."""
from django.core.management.base import BaseCommand

from apps.catalog.models import Product


class Command(BaseCommand):
    help = "Point products at /static/img/products/* so images work on Render"

    def handle(self, *args, **options):
        mapping = Product.STATIC_IMAGE_BY_SLUG
        updated = 0
        for product in Product.objects.all():
            static_url = mapping.get(product.slug)
            if not static_url:
                self.stdout.write(f"skip {product.slug or product.pk}: no bundled image")
                continue
            if product.image_url == static_url:
                continue
            product.image_url = static_url
            product.save(update_fields=["image_url"])
            updated += 1
            self.stdout.write(f"OK {product.slug} -> {static_url}")
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} product(s)"))
