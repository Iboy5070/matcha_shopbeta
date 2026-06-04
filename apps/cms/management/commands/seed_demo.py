from django.core.management.base import BaseCommand

from apps.cms.models import FAQItem, Testimonial


class Command(BaseCommand):
    help = "Seed demo testimonials and FAQ (idempotent)"

    def handle(self, *args, **options):
        testimonials = [
            {
                "company_name": "Goodmate",
                "quote_th": "เลือกมัทฉะของ MATCHAZUKI เพราะคุณภาพดี มีความเข้มข้น ผสมกับนมโอ๊ตแล้ว ยังได้รสและกลิ่นมัทฉะอยู่ ไม่โดนกลบ",
                "quote_en": "We chose MATCHAZUKI matcha for its quality and intensity — even with oat milk the matcha taste and aroma stay clear.",
                "sort_order": 1,
            },
            {
                "company_name": "Proove",
                "quote_th": "ผลตอบรับจากลูกค้าที่ลองโปรตีนรสมัทฉะ ที่ใช้ MATCHAZUKI ชื่นชอบกันมาก ๆ รสมัทฉะเข้มข้น หอมมาก",
                "quote_en": "Customers love our matcha protein made with MATCHAZUKI — rich, aromatic, truly premium.",
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
                "question_th": "สั่งซื้ออย่างไร?",
                "question_en": "How do I order?",
                "answer_th": "เลือกสินค้า ใส่ตะกร้า ชำระเงิน และแจ้งโอนผ่านหน้าแจ้งชำระเงิน",
                "answer_en": "Add items to cart, checkout, then submit your transfer slip on the payment notice page.",
                "sort_order": 1,
            },
            {
                "question_th": "จัดส่งกี่วัน?",
                "question_en": "How long is delivery?",
                "answer_th": "โดยทั่วไป 1–3 วันทำการหลังยืนยันการชำระเงิน",
                "answer_en": "Typically 1–3 business days after payment confirmation.",
                "sort_order": 2,
            },
        ]
        for data in faqs:
            FAQItem.objects.get_or_create(
                question_th=data["question_th"],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS("Demo CMS content ready."))
