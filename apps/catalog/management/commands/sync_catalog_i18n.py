from django.core.management.base import BaseCommand

from apps.catalog.i18n_sync import sync_catalog_i18n


class Command(BaseCommand):
    help = "Fill missing catalog TH/EN names (idempotent)"

    def handle(self, *args, **options):
        result = sync_catalog_i18n(only_missing=True)
        self.stdout.write(
            self.style.SUCCESS(
                "Catalog i18n synced — "
                f"categories: {result['categories']}, "
                f"products: {result['products']}, "
                f"variants: {result['variants']}"
            )
        )
