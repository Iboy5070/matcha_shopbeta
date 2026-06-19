from django.db import migrations


def fix_variant_weights(apps, schema_editor):
    ProductVariant = apps.get_model("catalog", "ProductVariant")
    for variant in ProductVariant.objects.all():
        dn = variant.display_name or ""
        if "100" in dn and variant.display_name_en == "30 g":
            variant.display_name_th = "100 กรัม"
            variant.display_name_en = "100 g"
            variant.save(update_fields=["display_name_th", "display_name_en"])


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_catalog_i18n"),
    ]

    operations = [
        migrations.RunPython(fix_variant_weights, migrations.RunPython.noop),
    ]
