from django.core.management.base import BaseCommand

from apps.cms.models import FAQItem, Testimonial


class Command(BaseCommand):
    help = "Seed demo testimonials and FAQ (idempotent)"

    def handle(self, *args, **options):
        testimonials = [
            {
                "company_name": "Goodmate",
                "quote_lo": "ເລືອກມັດຊາຂອງ The 196 Haus ເພາະຄຸນນະພາບດີ ເຂັ້ມຂຸ້ນ ຜົມກັບນົມໂອ໊ດແລ້ວ ຍັງໄດ້ລົດຊາດແລະກິ່ນມັດຊາຢູ່",
                "quote_th": "เลือกมัทฉะของ The 196 Haus เพราะคุณภาพดี มีความเข้มข้น ผสมกับนมโอ๊ตแล้ว ยังได้รสและกลิ่นมัทฉะอยู่ ไม่โดนกลบ",
                "quote_en": "We chose The 196 Haus matcha for its quality and intensity — even with oat milk the matcha taste and aroma stay clear.",
                "sort_order": 1,
            },
            {
                "company_name": "Proove",
                "quote_lo": "ລູກຄ້າຊອບໂປຣຕີນລົດມັດຊາທີ່ໃຊ້ The 196 Haus ຫຼາຍ — ເຂັ້ມຂຸ້ນ ຫອມ ຮູ້ສຶກເຖິງຄວາມພຣີເມຍມຈິງໆ",
                "quote_th": "ผลตอบรับจากลูกค้าที่ลองโปรตีนรสมัทฉะ ที่ใช้ The 196 Haus ชื่นชอบกันมาก ๆ รสมัทฉะเข้มข้น หอมมาก รู้สึกได้ถึงความพรีเมียมจริง ๆ",
                "quote_en": "Customers love our matcha protein made with The 196 Haus — rich, aromatic, truly premium.",
                "sort_order": 2,
            },
            {
                "company_name": "BUSABA Cafe & Bake Lab",
                "quote_lo": "ເປັນມັດຊາຄຸນນະພາບ ເຂັ້ມຂຸ້ນ ເອົາໄປທຳຂະໜົມຕໍ່ໄດ້ງ່າຍ ອຣ່ອຍ",
                "quote_th": "เราให้ความสำคัญกับทุกวัตถุดิบที่ใช้ พอได้ลองของ The 196 Haus ก็รู้ได้ว่าเป็นมัทฉะคุณภาพ เข้มข้น เลือกมาใช้ทำขนมต่อได้ง่าย อร่อย",
                "quote_en": "High-quality, intense matcha — easy to use in our bakery products.",
                "sort_order": 3,
            },
            {
                "company_name": "Craftsman Roastery",
                "quote_lo": "ມັດຊາຂອງ The 196 Haus ຕອບໂຈທຍ໌ຮ້ານທີ່ຕ້ອງການຊູລົດຊາດວັດຖຸດິບໂດຍບໍ່ຕ້ອງປຸງແຕ່ງຫຼາຍ ກໍຍັງອຣ່ອຍ ລູກຄ້າຊອບຄືຈົບ",
                "quote_th": "มัทฉะของ The 196 Haus ตอบโจทย์แนวคิดของร้านที่ต้องการชูรสชาติวัตถุดิบออกมาโดยไม่ต้องปรุงแต่งเยอะ ก็ยังอร่อย ลูกค้าชอบคือจบ",
                "quote_en": "The 196 Haus matcha fits our focus on ingredient flavor — delicious without heavy tweaking. Customers love it.",
                "sort_order": 4,
            },
        ]
        for data in testimonials:
            obj, created = Testimonial.objects.get_or_create(
                company_name=data["company_name"],
                defaults=data,
            )
            if not created:
                for key, value in data.items():
                    if key != "company_name":
                        setattr(obj, key, value)
                obj.save()

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
            {
                "question_lo": "ຊຳລະເງິນແບບໃດ?",
                "answer_lo": "ໂອນເງິນຜ່ານບັນຊີທະນາຄານ (BCEL / LAO QR) ຕາມລາຍລະອຽດໃນໜ້າ Checkout",
                "question_th": "ชำระเงินอย่างไร?",
                "question_en": "What payment methods do you accept?",
                "answer_th": "โอนเงินผ่านบัญชีธนาคาร (BCEL / LAO QR) ตามรายละเอียดในหน้า Checkout",
                "answer_en": "Bank transfer (BCEL / LAO QR) — details shown at checkout.",
                "sort_order": 3,
            },
            {
                "question_lo": "ແຈ້ງໂອນເງິນແນວໃດ?",
                "answer_lo": "ຫຼັງໂອນແລ້ວ ໄປໜ້າ «ແຈ້ງຊຳລະເງິນ» ໃສ່ເລກອໍເດີ ແລະອັບໂຫຼດຮູບສลິບ — ຮ້ານຈະກວດແລະຢືນຢັນພາຍໃນ 24 ຊມ.",
                "question_th": "แจ้งโอนเงินอย่างไร?",
                "question_en": "How do I confirm my bank transfer?",
                "answer_th": "หลังโอนแล้ว ไปหน้า «แจ้งชำระเงิน» ใส่เลขออเดอร์ และอัปโหลดสลิป — ร้านจะตรวจและยืนยันภายใน 24 ชม.",
                "answer_en": "After transferring, open Payment notice, enter your order number, and upload your slip. We verify within 24 hours.",
                "sort_order": 4,
            },
            {
                "question_lo": "ຈັດສົ່ງໄປໃສໄດ້?",
                "answer_lo": "ຈັດສົ່ງທົ່ວປະເທດລາວ — ຄ່າຈັດສົ່ງຄິດຕາມພື້ນທີ່ (ລາຍລະອຽດແຈ້ງຕອນຢືນຢັນອໍເດີ)",
                "question_th": "จัดส่งไปที่ไหนได้?",
                "question_en": "Where do you deliver?",
                "answer_th": "จัดส่งทั่วประเทศลาว — ค่าจัดส่งคิดตามพื้นที่ (แจ้งรายละเอียดเมื่อยืนยันออเดอร์)",
                "answer_en": "Nationwide delivery in Laos. Shipping cost depends on location — we confirm when verifying your order.",
                "sort_order": 5,
            },
            {
                "question_lo": "ເກັບຮັກສາຜົງມັດຊາແນວໃດ?",
                "answer_lo": "ປິດຝາສນິດ ກັນຄວາມຊຸ່ນ ແລະແສງແດດ — ເກັບໃນຕູ້ເຢັນ (0–5°C) ຫຼັງເປີດໃຊ້",
                "question_th": "เก็บรักษาผงมัทฉะอย่างไร?",
                "question_en": "How should I store matcha powder?",
                "answer_th": "ปิดฝาให้สนิท กันความชื้นและแสงแดด — เก็บในตู้เย็น (0–5°C) หลังเปิดใช้",
                "answer_en": "Keep sealed, away from moisture and sunlight. Refrigerate (0–5°C) after opening.",
                "sort_order": 6,
            },
            {
                "question_lo": "ມີຂາຍສົ່ງ / ຮ້ານຄາເຟບໍ?",
                "answer_lo": "ມີ — ຕິດຕໍ່ WhatsApp ຫຼືໜ້າຕິດຕໍ່ເພື່ອຂໍໃບລາຄາຂາຍສົ່ງ",
                "question_th": "มีขายส่ง / ร้านคาเฟไหม?",
                "question_en": "Do you offer wholesale or cafe supply?",
                "answer_th": "มี — ติดต่อ WhatsApp หรือหน้าติดต่อเพื่อขอใบเสนอราคาขายส่ง",
                "answer_en": "Yes — contact us via WhatsApp or the contact page for wholesale pricing.",
                "sort_order": 7,
            },
            {
                "question_lo": "ຕິດຕໍ່ຮ້ານແນວໃດ?",
                "answer_lo": "ໜ້າຕິດຕໍ່, WhatsApp, ຫຼື Facebook — ລະບຸເລກອໍເດີເມື່ອຖາມເລື່ອງການສັ່ງຊື້",
                "question_th": "ติดต่อร้านอย่างไร?",
                "question_en": "How can I reach customer support?",
                "answer_th": "หน้าติดต่อ, WhatsApp หรือ Facebook — ระบุเลขออเดอร์เมื่อถามเรื่องการสั่งซื้อ",
                "answer_en": "Contact page, WhatsApp, or Facebook. Include your order number for order-related questions.",
                "sort_order": 8,
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
