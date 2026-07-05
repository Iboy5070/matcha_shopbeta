import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

migrations_to_fake = [
    ("catalog", "0002_category_slug_product_image_product_is_featured_and_more"),
    ("catalog", "0003_populate_slugs"),
    ("catalog", "0004_slug_unique"),
    ("catalog", "0005_product_image_url"),
    ("catalog", "0006_catalog_i18n"),
    ("catalog", "0007_fix_variant_i18n"),
    ("catalog", "0008_resync_catalog_i18n"),
    ("catalog", "0009_productvariant_image_url"),
    ("catalog", "0010_alter_category_name_alter_product_description_and_more"),
    ("cms", "0001_initial"),
    ("cms", "0002_faq_lao_fields"),
    ("cms", "0003_populate_faq_lao"),
    ("cms", "0004_testimonial_quote_lo"),
    ("inventory", "0002_alter_stockmovement_actor_and_more"),
    ("sales", "0002_order_updated_at_alter_order_order_no_and_more"),
    ("store", "0002_customer_profile"),
    ("store", "0003_paymentconfirmation_slip_url"),
    ("store", "0004_alter_weborder_status")
]

with connection.cursor() as cursor:
    for app, name in migrations_to_fake:
        # Check if exists
        cursor.execute("SELECT id FROM django_migrations WHERE app=%s AND name=%s", [app, name])
        if not cursor.fetchone():
            print(f"Faking {app}.{name}")
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                [app, name]
            )

print("Done faking migrations in DB.")
