from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    for cat in Category.objects.all():
        if not cat.slug:
            base = slugify(cat.name) or "category"
            slug = base
            n = 1
            while Category.objects.filter(slug=slug).exclude(pk=cat.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            cat.slug = slug
            cat.save(update_fields=["slug"])

    for product in Product.objects.all():
        if not product.slug:
            base = slugify(product.name) or "product"
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=product.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            product.slug = slug
            product.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_category_slug_product_image_product_is_featured_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]
