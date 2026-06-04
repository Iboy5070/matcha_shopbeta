from django.db import migrations, models


class Migration(migrations.Migration):
    """
    After 0003 populates all slugs, enforce unique + not-null.
    """

    dependencies = [
        ("catalog", "0003_populate_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="slug",
            field=models.SlugField(max_length=120, unique=True, blank=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(max_length=220, unique=True, blank=True),
        ),
    ]
