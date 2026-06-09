from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0004_slug_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_url",
            field=models.URLField(
                blank=True,
                help_text="ລິ້ງຮູບຈາກ CDN (ແນະນຳສຳລັບ production — ບໍ່ຫາຍເມື່ອ deploy)",
            ),
        ),
    ]
