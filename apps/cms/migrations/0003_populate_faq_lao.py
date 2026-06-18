from django.db import migrations

FAQ_LO = {
    1: {
        "question_lo": "ສັ່ງຊື້ຢ່າງໃດ?",
        "answer_lo": "ເລືອກສິນຄ້າ ໃສ່ກະຕ່າ ຊຳລະເງິນ ແລະແຈ້ງໂອນຜ່ານໜ້າແຈ້ງຊຳລະເງິນ",
        "question_th": "สั่งซื้ออย่างไร?",
        "answer_th": "เลือกสินค้า ใส่ตะกร้า ชำระเงิน และแจ้งโอนผ่านหน้าแจ้งชำระเงิน",
    },
    2: {
        "question_lo": "ຈັດສົ່ງກີ່ວັນ?",
        "answer_lo": "ໂດຍທົ່ວໄປ 1–3 ວັນເຮັດວຽນຫຼັງຢືນຢັນການຊຳລະເງິນ",
        "question_th": "จัดส่งกี่วัน?",
        "answer_th": "โดยทั่วไป 1–3 วันทำการหลังยืนยันการชำระเงิน",
    },
}


def populate_faq(apps, schema_editor):
    FAQItem = apps.get_model("cms", "FAQItem")
    for sort_order, data in FAQ_LO.items():
        rows = FAQItem.objects.filter(sort_order=sort_order).order_by("id")
        if not rows.exists():
            continue
        item = rows.first()
        for key, value in data.items():
            setattr(item, key, value)
        item.save(update_fields=list(data.keys()))


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0002_faq_lao_fields"),
    ]

    operations = [
        migrations.RunPython(populate_faq, migrations.RunPython.noop),
    ]
