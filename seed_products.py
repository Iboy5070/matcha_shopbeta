import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.catalog.models import Category, Product
from apps.inventory.models import Inventory

Category.objects.all().delete()
Product.objects.all().delete()

matcha_cat = Category.objects.create(name="Matcha", name_th="ມັດຊະ", name_en="Matcha", slug="matcha")
tea_cat = Category.objects.create(name="Tea", name_th="ຊາ", name_en="Tea", slug="tea")
equip_cat = Category.objects.create(name="Equipment", name_th="ອຸປະກອນ", name_en="Equipment", slug="equipment")

products = [
    {
        "category": matcha_cat,
        "name": "Ceremonial Grade Matcha",
        "name_en": "Ceremonial Grade Matcha",
        "description": "ຜົງມັດຊາເກຣດ ceremonial ຈາກຍີ່ປຸ່ນ — ສີຂຽວສົດ ກິ່ນຫອມຫຍ້າ ລົດນຸ້ມຂົມນ້ອຍ. ເໝາະດື່ມເປັນຈອກຕາມວິທີດັ້ງເດີມ ຫຼື latte ພິເສດ.",
        "description_en": "Ceremonial grade matcha — bright green, grassy aroma, smooth. Ideal for traditional bowls or a premium latte.",
        "price": 250000.00,
        "slug": "ceremonial-matcha",
        "image_url": "/static/img/products/matcha-ceremonial-50g.jpg",
        "stock_qty": 24,
        "is_active": True,
        "is_featured": True,
    },
    {
        "category": matcha_cat,
        "name": "Culinary Grade Matcha",
        "name_en": "Culinary Grade Matcha",
        "description": "ມັດຊາສຳລັບເຮັດເຄື່ອງດື່ມ ແລະ ເຂົ້າໜົມ — ລົດຊັດ ລາຄາດີ ທັນສະໄໝສຳລັບຄົວເຮືອນ ແລະ ຮ້ານກາເຟ. ໃຊ້ໄດ້ກັບນົມ, ນ້ຳຕານ, ແລະ ສູດເຂົ້າໜົມ.",
        "description_en": "Culinary matcha for lattes, baking and smoothies — bold flavor, modern kitchen staple.",
        "price": 120000.00,
        "slug": "culinary-matcha",
        "image_url": "/static/img/products/matcha-premium-30g.jpg",
        "stock_qty": 40,
        "is_active": True,
        "is_featured": True,
    },
    {
        "category": tea_cat,
        "name": "Houjicha Roasted Tea",
        "name_en": "Houjicha Roasted Tea",
        "description": "ຊາຂຽວຄັວຍ ກິ່ນຫອມອົບອຸ່ນ · ຄາເຟອີນຕ່ຳ — ດື່ມໄດ້ທຸກເວລາ ທັງຮ້ອນແລະເຢັນ.",
        "description_en": "Roasted green tea with warm aroma and low caffeine — great hot or iced.",
        "price": 150000.00,
        "slug": "houjicha",
        "image_url": "/static/img/products/matcha-classic-100g.jpg",
        "stock_qty": 16,
        "is_active": True,
        "is_featured": True,
    },
    {
        "category": equip_cat,
        "name": "Bamboo Whisk (Chasen)",
        "name_en": "Bamboo Whisk (Chasen)",
        "description": "ໄມ້ຕີມັດຊາ (chasen) ເຮັດຈາກໄມ້ໄຜ່ — ຊ່ວຍໃຫ້ຜົງລະລາຍເປັນໂຟມນຸ້ມ ສຳລັບຈອກມັດຊາທີ່ເບິ່ງສວຍ.",
        "description_en": "Traditional bamboo chasen for whisking matcha into a smooth foam.",
        "price": 85000.00,
        "slug": "bamboo-whisk",
        "image_url": "/static/img/products/bamboo-whisk-chasen.jpg",
        "stock_qty": 30,
        "is_active": True,
        "is_featured": True,
    },
]

for p_data in products:
    data = dict(p_data)
    # stock_qty is set via an Inventory batch below (not directly on Product)
    # so the warehouse batch ledger (Admin → Inventory → Stock) always starts
    # in sync with the live sellable count instead of drifting apart.
    initial_stock = data.pop("stock_qty", 0)
    product = Product.objects.create(**data)
    if initial_stock:
        Inventory.objects.create(product=product, quantity=initial_stock)

print(f"Successfully seeded {len(products)} products in {Category.objects.count()} categories!")
