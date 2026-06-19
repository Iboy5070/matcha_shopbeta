from django.db import migrations

from apps.catalog.i18n_sync import sync_catalog_i18n


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0007_fix_variant_i18n"),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: sync_catalog_i18n(only_missing=True),
            migrations.RunPython.noop,
        ),
    ]
