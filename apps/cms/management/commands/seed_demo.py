from django.core.management.base import BaseCommand

from apps.cms.models import FAQItem, Testimonial


class Command(BaseCommand):
    help = "Seed demo testimonials and FAQ (idempotent)"

    def handle(self, *args, **options):
        testimonials = [
            {
                "company_name": "Goodmate",
                "quote_th": "เลือกมัทฉะของ The 196 Haus เพราะคุณภาพดี มีความเข้มข้น ผสมกับนมโอ๊ตแล้ว ยังได้รสและกลิ่นมัทฉะอยู่ ไม่โดนกลบ",
                "quote_en": "We chose The 196 Haus matcha for its quality and intensity — even with oat milk the matcha taste and aroma stay clear.",
                "sort_order": 1,
            },
            {
                "company_name": "Proove",
                "quote_th": "ผลตอบรับจากลูกค้าที่ลองโปรตีนรสมัทฉะ ที่ใช้ The 196 Haus ชื่นชอบกันมาก ๆ รสมัทฉะเข้มข้น หอมมาก",
                "quote_en": "Customers love our matcha protein made with The 196 Haus — rich, aromatic, truly premium.",
                "sort_order": 2,
            },
            {
                "company_name": "BUSABA Cafe & Bake Lab",
                "quote_th": "เป็นมัทฉะคุณภาพ เข้มข้น เลือกมาใช้ทำขนมต่อได้ง่าย อร่อย",
                "quote_en": "High-quality, intense matcha — easy to use in our bakery products.",
                "sort_order": 3,
            },
        ]
        for data in testimonials:
            Testimonial.objects.get_or_create(
                company_name=data["company_name"],
                defaults=data,
            )

        faqs = [
            {
                "question_lo": "ສັ່ງຊື້ຢ່າງໃດ?",
                "answer_lo": "ເລືອກສິນຄ້າ ໃສ່ກະຕ່າ ຊຳລະເງິນ ແລະແຈ້ງໂອນຜ່ານໜ້າແຈ້ງຊຳລະເງິນ",
                "question_th": "สั่งซื้ออย่างไร?",
                "question_en": "How do I order?",
                "answer_th": "เลือกสินค้า ใส่ตะกร้า ชำระเงิน และแจ้งโอนผ่านหน้าแจ้งชำระเงิน",
                "answer_en": "Add items to cart, checkout, then submit your transfer slip on the payment notice page.",
                "sort_order": 1,
            },
            {
                "question_lo": "ຈັດສົ່ງກີ່ວັນ?",
                "answer_lo": "ໂດຍທົ່ວໄປ 1–3 ວັນເຮັດວຽນຫຼັງຢືນຢັນການຊຳລະເງິນ",
                "question_th": "จัดส่งกี่วัน?",
                "question_en": "How long is delivery?",
                "answer_th": "โดยทั่วไป 1–3 วันทำการหลังยืนยันการชำระเงิน",
                "answer_en": "Typically 1–3 business days after payment confirmation.",
                "sort_order": 2,
            },
        ]
        for data in faqs:
            rows = FAQItem.objects.filter(sort_order=data["sort_order"]).order_by("id")
            if rows.exists():
                item = rows.first()
                for key, value in data.items():
                    setattr(item, key, value)
                item.save()
                rows.exclude(pk=item.pk).delete()
            else:
                FAQItem.objects.create(**data)

        self.stdout.write(self.style.SUCCESS("Demo CMS content ready."))
