from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        # slug fields: null=True first so existing rows don't violate UNIQUE
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=120, blank=True, null=True, unique=False),
        ),
        migrations.AddField(
            model_name="product",
            name="slug",
            field=models.SlugField(max_length=220, blank=True, null=True, unique=False),
        ),
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, upload_to="products/"),
        ),
        migrations.AddField(
            model_name="product",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
    ]
