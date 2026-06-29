from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.catalog.i18n_sync import sync_catalog_i18n
from apps.catalog.models import Category, Product, ProductVariant


def _static_image(path: str) -> str:
    base = (getattr(settings, "SITE_URL", "") or "https://matcha-shopbeta.onrender.com").rstrip("/")
    return f"{base}/static/{path.lstrip('/')}"


CEREMONIAL_IMAGE = (
    "https://getcrafti.co/cdn/shop/files/Ceremonialmatcha30gnobg.png?v=1737512532"
)
CRAFTI_CUP_IMAGE = (
    "https://getcrafti.co/cdn/shop/files/Crafti_Cup_among_leaves-3_web_res.jpg"
)
CULINARY_IMAGE = _static_image("p.jpg")
LATTE_IMAGE = CRAFTI_CUP_IMAGE
ICED_IMAGE = _static_image("f1.jpg")
HOJICHA_IMAGE = _static_image("f2.png")
CHASEN_IMAGE = (
    "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop"
)
CHAWAN_IMAGE = (
    "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=600&auto=format&fit=crop"
)

CATEGORIES = [
    {
        "slug": "matcha-powder",
        "name": "ຜົງມັດຊາ",
        "name_th": "ผงมัทฉะ",
        "name_en": "Matcha powder",
    },
    {
        "slug": "matcha-drinks",
        "name": "ເຄື່ອງດື່ມມັດຊາ",
        "name_th": "เครื่องดื่มมัทฉะ",
        "name_en": "Matcha drinks",
    },
    {
        "slug": "equipment",
        "name": "ອຸປະກອນຊົງມັດຊາ",
        "name_th": "อุปกรณ์ชงมัทฉะ",
        "name_en": "Tools & accessories",
    },
]

PRODUCTS = [
    {
        "slug": "ceremonial-matcha",
        "category": "matcha-powder",
        "name": "ມັດຊາ ເກຣດ Ceremonial",
        "name_th": "มัทฉะเกรด Ceremonial",
        "name_en": "Ceremonial Grade Matcha",
        "description": "ມັດຊາເກຣດ Ceremonial organic — ສີຂຽວສົດ หอม umami",
        "description_th": "มัทฉะเกรด Ceremonial organic — 30g",
        "description_en": "Organic ceremonial grade matcha — rich umami",
        "image_url": CEREMONIAL_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "MATCHA-CER-30",
                "display_name": "30 ກຣາມ",
                "display_name_th": "30 กรัม",
                "display_name_en": "30 g",
                "weight_g": 30,
                "sell_price": Decimal("49000"),
                "stock_qty": 100,
            },
            {
                "sku": "MATCHA-CER-50",
                "display_name": "50 ກຣາມ",
                "display_name_th": "50 กรัม",
                "display_name_en": "50 g",
                "weight_g": 50,
                "sell_price": Decimal("75000"),
                "stock_qty": 80,
            },
        ],
    },
    {
        "slug": "matcha-culinary-premium",
        "category": "matcha-powder",
        "name": "ມັດຊາ ເກຣດ Culinary Premium",
        "name_th": "มัทฉะเกรด Culinary พรีเมียม",
        "name_en": "Culinary Grade Premium Matcha",
        "description": "ເຫມາະສຳລັບຂນม, เครื่องดื่ม, และลาเต้",
        "description_th": "มัทฉะเกรด Culinary สำหรับขนมและเครื่องดื่ม",
        "description_en": "Premium culinary grade matcha for baking and drinks",
        "image_url": CULINARY_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "MATCHA-CUL-100",
                "display_name": "100 ກຣາມ",
                "display_name_th": "100 กรัม",
                "display_name_en": "100 g",
                "weight_g": 100,
                "sell_price": Decimal("65000"),
                "stock_qty": 60,
            },
        ],
    },
    {
        "slug": "matcha-latte-blend",
        "category": "matcha-powder",
        "name": "ມັດຊາລາເຕ້ Blend",
        "name_th": "มัทฉะลาเต้ Blend",
        "name_en": "Matcha Latte Blend",
        "description": "ສູດຜົງມັດຊາສຳລັບລາເຕ້ — หอมนุ่ม ละลายง่าย",
        "description_th": "สูตรมัทฉะลาเต้ หอมนุ่ม",
        "description_en": "Smooth blend crafted for matcha lattes",
        "image_url": LATTE_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "MATCHA-LAT-30",
                "display_name": "30 ກຣາມ",
                "display_name_th": "30 กรัม",
                "display_name_en": "30 g",
                "weight_g": 30,
                "sell_price": Decimal("42000"),
                "stock_qty": 90,
            },
        ],
    },
    {
        "slug": "iced-matcha",
        "category": "matcha-drinks",
        "name": "ມັດຊາເຢັນ (ຜົງຊົງ)",
        "name_th": "มัทฉะเย็น",
        "name_en": "Iced Matcha Mix",
        "description": "ຜົງມັດຊາສຳລັບມັດຊາເຢັນ — สดชื่น เข้มข้น",
        "description_th": "มัทฉะเย็นเข้มข้น หอมสดชื่น",
        "description_en": "Rich, refreshing iced matcha mix",
        "image_url": ICED_IMAGE,
        "is_featured": False,
        "variants": [
            {
                "sku": "MATCHA-ICE-30",
                "display_name": "30 ກຣາມ",
                "display_name_th": "30 กรัม",
                "display_name_en": "30 g",
                "weight_g": 30,
                "sell_price": Decimal("38000"),
                "stock_qty": 70,
            },
        ],
    },
    {
        "slug": "hojicha-powder",
        "category": "matcha-powder",
        "name": "ຜົງໂຮຈິຊາ",
        "name_th": "ผงโฮจิชา",
        "name_en": "Hojicha Powder",
        "description": "ຊາໂຮຈິຊາຄັ່ນ — กลิ่นหอม รสนุ่ม",
        "description_th": "ชาโฮจิชาคั่ว กลิ่นหอม",
        "description_en": "Roasted hojicha powder with a warm aroma",
        "image_url": HOJICHA_IMAGE,
        "is_featured": False,
        "variants": [
            {
                "sku": "HOJICHA-50",
                "display_name": "50 ກຣາມ",
                "display_name_th": "50 กรัม",
                "display_name_en": "50 g",
                "weight_g": 50,
                "sell_price": Decimal("45000"),
                "stock_qty": 50,
            },
        ],
    },
    {
        "slug": "chasen-whisk",
        "category": "equipment",
        "name": "ເຊັນຕີມັດຊາ (ໄມ້ໄຜ່ 80 ແຉກ)",
        "name_th": "ชาเซ็น (ไม้ไผ่ 80 แฉก)",
        "name_en": "Bamboo Whisk (80 prongs)",
        "description": "ອຸປະກອນຕີມັດຊາແບບດັ້ງເດີມ — ไม้ไผ่แท้",
        "description_th": "ที่ตีมัทฉะไม้ไผ่แท้",
        "description_en": "Traditional bamboo matcha whisk",
        "image_url": CHASEN_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "TOOL-CHASEN",
                "display_name": "1 ຊິ້ນ",
                "display_name_th": "1 ชิ้น",
                "display_name_en": "1 pc",
                "sell_price": Decimal("85000"),
                "stock_qty": 30,
            },
        ],
    },
    {
        "slug": "chawan-bowl",
        "category": "equipment",
        "name": "ຊາວັນ (ຖ້ວຍຊົງມັດຊາ)",
        "name_th": "ชawan (ถ้วยชงมัทฉะ)",
        "name_en": "Matcha Bowl (Chawan)",
        "description": "ຖ້ວຍຊົງມັດຊາສໄຕລ໌ຍີ່ປຸ່ນ — เหมาะสำหรับพิธีชง",
        "description_th": "ถ้วยชงมัทฉะสไตล์ญี่ปุ่น",
        "description_en": "Japanese-style bowl for preparing matcha",
        "image_url": CHAWAN_IMAGE,
        "is_featured": False,
        "variants": [
            {
                "sku": "TOOL-CHAWAN",
                "display_name": "1 ຊິ້ນ",
                "display_name_th": "1 ชิ้น",
                "display_name_en": "1 pc",
                "sell_price": Decimal("120000"),
                "stock_qty": 20,
            },
        ],
    },
    {
        "slug": "matcha-capsule",
        "category": "matcha-drinks",
        "name": "ມັດຊາ Capsule (10 ແຄບຊູນ)",
        "name_th": "มัทฉะแคปซูล (10 แคปซูล)",
        "name_en": "Matcha Capsule (10 pcs)",
        "description": "ມັດຊາຍີ່ປຸ່ນໃນແຄບຊູນ — ໃຊ້ກັບເຄື່ອງ Nespresso",
        "description_th": "มัทฉะญี่ปุ่นในแคปซูล — ใช้กับเครื่อง Nespresso",
        "description_en": "Japanese matcha capsules for Nespresso machines",
        "image_url": CEREMONIAL_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "CAP-EX-10",
                "display_name": "Excellent Rich ×10",
                "display_name_th": "Excellent Rich ×10",
                "display_name_en": "Excellent Rich ×10",
                "image_url": CEREMONIAL_IMAGE,
                "sell_price": Decimal("55000"),
                "stock_qty": 40,
            },
            {
                "sku": "CAP-MD-10",
                "display_name": "Medium Rich ×10",
                "display_name_th": "Medium Rich ×10",
                "display_name_en": "Medium Rich ×10",
                "image_url": CRAFTI_CUP_IMAGE,
                "sell_price": Decimal("48000"),
                "stock_qty": 45,
            },
            {
                "sku": "CAP-CL-10",
                "display_name": "Classic Rich ×10",
                "display_name_th": "Classic Rich ×10",
                "display_name_en": "Classic Rich ×10",
                "image_url": CULINARY_IMAGE,
                "sell_price": Decimal("42000"),
                "stock_qty": 50,
            },
        ],
    },
    {
        "slug": "genmaicha-powder",
        "category": "matcha-powder",
        "name": "ຜົງ Genmaicha",
        "name_th": "ผงเกนmaicha",
        "name_en": "Genmaicha Powder",
        "description": "ຊາເຂົ້າຄົ່ມັດຊາ — ກລິ່ນຫອມ รสกลมกล่อม",
        "description_th": "ชาเกนmaicha ผสมข้าวคั่ว",
        "description_en": "Roasted rice and green tea blend powder",
        "image_url": _static_image("f3.jpg"),
        "is_featured": False,
        "variants": [
            {
                "sku": "GENMAICHA-80",
                "display_name": "80 ກຣາມ",
                "display_name_th": "80 กรัม",
                "display_name_en": "80 g",
                "weight_g": 80,
                "sell_price": Decimal("52000"),
                "stock_qty": 35,
            },
        ],
    },
    {
        "slug": "matcha-starter-set",
        "category": "equipment",
        "name": "Matcha Starter Set",
        "name_th": "ชุดเริ่มต้นชงมัทฉะ",
        "name_en": "Matcha Starter Set",
        "description": "ເຊັນ + ຊາວັນ + ຊີວ Chashaku — ພ້ອມເລີ່ມຊົງ",
        "description_th": "ชาเซ็น + ชawan + ช้อนตวง — พร้อมเริ่มชง",
        "description_en": "Whisk, bowl, and scoop — everything to begin",
        "image_url": CHAWAN_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "SET-STARTER",
                "display_name": "1 ຊຸດ",
                "display_name_th": "1 ชุด",
                "display_name_en": "1 set",
                "sell_price": Decimal("185000"),
                "stock_qty": 15,
            },
        ],
    },
    {
        "slug": "matcha-rich-blend",
        "category": "matcha-powder",
        "name": "Matcha Rich (ສຳລັບຮ້ານ)",
        "name_th": "มัทฉะริช (สำหรับร้าน)",
        "name_en": "Matcha Rich (for cafés)",
        "description": "ສູດມັດຊາເຂັ້ມ — ເຫມາະສຳລັບຮ້ານກາເຟ ແລະ ຊານม",
        "description_th": "สูตรมัทฉะเข้ม — เหมาะสำหรับร้านกาแฟ",
        "description_en": "Rich blend crafted for cafés and bubble tea shops",
        "image_url": LATTE_IMAGE,
        "is_featured": True,
        "variants": [
            {
                "sku": "RICH-100",
                "display_name": "100 ກຣາມ",
                "display_name_th": "100 กรัม",
                "display_name_en": "100 g",
                "weight_g": 100,
                "sell_price": Decimal("72000"),
                "stock_qty": 40,
            },
            {
                "sku": "RICH-200",
                "display_name": "200 ກຣາມ",
                "display_name_th": "200 กรัม",
                "display_name_en": "200 g",
                "weight_g": 200,
                "sell_price": Decimal("128000"),
                "stock_qty": 25,
            },
        ],
    },
]


CANONICAL_PRODUCT_SLUGS = {item["slug"] for item in PRODUCTS}
CANONICAL_CATEGORY_SLUGS = {item["slug"] for item in CATEGORIES}


def _remove_legacy_catalog():
    """Remove duplicate pre-seed products; keep hidden if tied to past orders."""
    from apps.sales.models import OrderItem
    from apps.store.models import WebOrderItem

    legacy = Product.objects.exclude(slug__in=CANONICAL_PRODUCT_SLUGS)
    deleted = 0
    hidden = 0
    for product in legacy:
        variant_ids = list(product.variants.values_list("id", flat=True))
        has_orders = (
            WebOrderItem.objects.filter(variant_id__in=variant_ids).exists()
            or OrderItem.objects.filter(variant_id__in=variant_ids).exists()
        )
        if has_orders:
            product.is_active = False
            product.is_featured = False
            product.save(update_fields=["is_active", "is_featured"])
            product.variants.update(is_active=False)
            hidden += 1
        else:
            product.delete()
            deleted += 1
    return deleted, hidden


def _upsert_category(data):
    cat, _ = Category.objects.get_or_create(
        slug=data["slug"],
        defaults={
            "name": data["name"],
            "name_th": data["name_th"],
            "name_en": data["name_en"],
        },
    )
    changed = []
    for field in ("name", "name_th", "name_en"):
        if getattr(cat, field) != data[field]:
            setattr(cat, field, data[field])
            changed.append(field)
    if changed:
        cat.save(update_fields=changed)
    return cat


def _upsert_product(data, category):
    product, created = Product.objects.get_or_create(
        slug=data["slug"],
        defaults={
            "category": category,
            "name": data["name"],
            "name_th": data["name_th"],
            "name_en": data["name_en"],
            "description": data["description"],
            "description_th": data["description_th"],
            "description_en": data["description_en"],
            "image_url": data["image_url"],
            "is_featured": data["is_featured"],
            "is_active": True,
        },
    )
    if not created:
        product.category = category
        product.name = data["name"]
        product.name_th = data["name_th"]
        product.name_en = data["name_en"]
        product.description = data["description"]
        product.description_th = data["description_th"]
        product.description_en = data["description_en"]
        product.image_url = data["image_url"]
        product.is_featured = data["is_featured"]
        product.is_active = True
        product.save()
    return product


def _upsert_variant(product, data):
    price = data["sell_price"]
    image_url = data.get("image_url", "")
    variant, created = ProductVariant.objects.get_or_create(
        sku=data["sku"],
        defaults={
            "product": product,
            "display_name": data["display_name"],
            "display_name_th": data["display_name_th"],
            "display_name_en": data["display_name_en"],
            "weight_g": data.get("weight_g"),
            "price": price,
            "sell_price": price,
            "stock_qty": data["stock_qty"],
            "image_url": image_url,
            "is_active": True,
        },
    )
    if not created:
        variant.product = product
        variant.display_name = data["display_name"]
        variant.display_name_th = data["display_name_th"]
        variant.display_name_en = data["display_name_en"]
        variant.weight_g = data.get("weight_g")
        variant.price = price
        variant.sell_price = price
        variant.stock_qty = data["stock_qty"]
        variant.image_url = image_url
        variant.is_active = True
        variant.save()
    return variant


class Command(BaseCommand):
    help = "Seed catalog products + categories (idempotent)"

    def handle(self, *args, **options):
        categories = {}
        for cat_data in CATEGORIES:
            categories[cat_data["slug"]] = _upsert_category(cat_data)

        product_count = 0
        variant_count = 0
        for item in PRODUCTS:
            category = categories[item["category"]]
            product = _upsert_product(item, category)
            product_count += 1
            for variant_data in item["variants"]:
                _upsert_variant(product, variant_data)
                variant_count += 1

        sync_catalog_i18n()
        deleted, hidden = _remove_legacy_catalog()
        extra = []
        if deleted:
            extra.append(f"{deleted} legacy deleted")
        if hidden:
            extra.append(f"{hidden} legacy hidden")
        suffix = f", {', '.join(extra)}" if extra else ""

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog ready — {len(CATEGORIES)} categories, "
                f"{product_count} products, {variant_count} variants{suffix}."
            )
        )
