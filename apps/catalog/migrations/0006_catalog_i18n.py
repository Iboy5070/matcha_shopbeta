from django.db import migrations, models


def populate_catalog_i18n(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")
    ProductVariant = apps.get_model("catalog", "ProductVariant")

    category_map = {
        "matcha-powder": ("ผงมัทฉะ", "Matcha powder"),
    }
    for slug, (name_th, name_en) in category_map.items():
        Category.objects.filter(slug=slug).update(name_th=name_th, name_en=name_en)

    for cat in Category.objects.filter(name_th=""):
        if "ຜົງ" in cat.name or "powder" in (cat.slug or ""):
            cat.name_th = "ผงมัทฉะ"
            cat.name_en = "Matcha powder"
            cat.save(update_fields=["name_th", "name_en"])
        elif cat.name in ("ມັດຊະ", "ມັດຊາ") or cat.slug in ("matcha", "matcha-drinks"):
            cat.name_th = "มัทฉะ"
            cat.name_en = "Matcha"
            cat.save(update_fields=["name_th", "name_en"])

    product_updates = {
        "ceremonial-matcha": {
            "name_th": "มัทฉะเกรด Ceremonial",
            "name_en": "Ceremonial Grade Matcha",
            "description_th": "มัทฉะเกรด Ceremonial organic — 30g",
            "description_en": "Organic ceremonial grade matcha — 30g",
        },
        "iced-matcha": {
            "name_th": "มัทฉะเย็น",
            "name_en": "Iced Matcha",
            "description_th": "มัทฉะเย็นเข้มข้น หอมสดชื่น",
            "description_en": "Rich, refreshing iced matcha",
        },
    }
    for slug, data in product_updates.items():
        Product.objects.filter(slug=slug).update(**data)

    for product in Product.objects.filter(name_th=""):
        name = product.name or ""
        slug = product.slug or ""
        if "Ceremonial" in name or "ceremonial" in slug:
            product.name_th = "มัทฉะเกรด Ceremonial"
            product.name_en = "Ceremonial Grade Matcha"
            if not product.description_th and product.description:
                product.description_th = "มัทฉะเกรด Ceremonial organic — 30g"
                product.description_en = "Organic ceremonial grade matcha — 30g"
            product.save(
                update_fields=["name_th", "name_en", "description_th", "description_en"]
            )
        elif "ມັດສະ" in name or "iced" in slug:
            product.name_th = "มัทฉะเย็น"
            product.name_en = "Iced Matcha"
            product.description_th = product.description_th or "มัทฉะเย็นเข้มข้น หอมสดชื่น"
            product.description_en = product.description_en or "Rich, refreshing iced matcha"
            product.save(
                update_fields=["name_th", "name_en", "description_th", "description_en"]
            )

    variant_updates = {
        "MATCHA-CER-30": ("30 กรัม", "30 g"),
    }
    for sku, (name_th, name_en) in variant_updates.items():
        ProductVariant.objects.filter(sku=sku).update(
            display_name_th=name_th, display_name_en=name_en
        )

    for variant in ProductVariant.objects.filter(display_name_th=""):
        dn = variant.display_name or ""
        if "100" in dn:
            variant.display_name_th = "100 กรัม"
            variant.display_name_en = "100 g"
            variant.save(update_fields=["display_name_th", "display_name_en"])
        elif "30" in dn or dn.strip() == "30 ກຣາມ":
            variant.display_name_th = "30 กรัม"
            variant.display_name_en = "30 g"
            variant.save(update_fields=["display_name_th", "display_name_en"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_product_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="name_en",
            field=models.CharField(blank=True, max_length=100, verbose_name="Name (EN)"),
        ),
        migrations.AddField(
            model_name="category",
            name="name_th",
            field=models.CharField(blank=True, max_length=100, verbose_name="ชื่อ (ไทย)"),
        ),
        migrations.AddField(
            model_name="product",
            name="description_en",
            field=models.TextField(blank=True, verbose_name="Description (EN)"),
        ),
        migrations.AddField(
            model_name="product",
            name="description_th",
            field=models.TextField(blank=True, verbose_name="คำอธิบาย (ไทย)"),
        ),
        migrations.AddField(
            model_name="product",
            name="name_en",
            field=models.CharField(blank=True, max_length=200, verbose_name="Name (EN)"),
        ),
        migrations.AddField(
            model_name="product",
            name="name_th",
            field=models.CharField(blank=True, max_length=200, verbose_name="ชื่อ (ไทย)"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="display_name_en",
            field=models.CharField(blank=True, max_length=120, verbose_name="Name (EN)"),
        ),
        migrations.AddField(
            model_name="productvariant",
            name="display_name_th",
            field=models.CharField(blank=True, max_length=120, verbose_name="ชื่อ (ไทย)"),
        ),
        migrations.RunPython(populate_catalog_i18n, migrations.RunPython.noop),
    ]
