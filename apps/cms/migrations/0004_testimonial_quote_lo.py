from django.db import migrations, models


def copy_th_to_lo(apps, schema_editor):
    Testimonial = apps.get_model("cms", "Testimonial")
    for row in Testimonial.objects.filter(quote_lo=""):
        row.quote_lo = row.quote_th
        row.save(update_fields=["quote_lo"])


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0003_populate_faq_lao"),
    ]

    operations = [
        migrations.AddField(
            model_name="testimonial",
            name="quote_lo",
            field=models.TextField(blank=True, verbose_name="ຄຳເຫັນ (ລາວ)"),
        ),
        migrations.AlterField(
            model_name="testimonial",
            name="quote_en",
            field=models.TextField(blank=True, verbose_name="Quote (EN)"),
        ),
        migrations.AlterField(
            model_name="testimonial",
            name="quote_th",
            field=models.TextField(verbose_name="ຄຳເຫັນ (ไทย)"),
        ),
        migrations.RunPython(copy_th_to_lo, migrations.RunPython.noop),
    ]
