from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_resync_catalog_i18n"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="image_url",
            field=models.URLField(
                blank=True,
                help_text="Optional — overrides product image for this option (e.g. size/grade).",
                verbose_name="Variant image URL",
            ),
        ),
    ]
