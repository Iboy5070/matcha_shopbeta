from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_customer_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentconfirmation",
            name="slip_url",
            field=models.URLField(blank=True, verbose_name="Slip URL (cloud)"),
        ),
    ]
