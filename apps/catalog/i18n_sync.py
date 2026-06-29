"""Idempotent catalog i18n defaults — run via migrate or management command."""

from django.db.models import Q

# Lao markers copied from production seed / migration patterns
LAO_ICED = "ມັດສະ"
LAO_MATCHA_CAT = ("ມັດຊະ", "ມັດຊາ", "ມັດສະ")
LAO_COLD = "ເຢັນ"
LAO_LATTE = "ລາເຕ້"
LAO_HOJICHA = "ໂຮຈິຊາ"
LAO_CHASEN = "ເຊັນ"
LAO_CHAWAN = "ຊາວັນ"
LAO_GRAM = "ກຣາມ"

PRODUCT_BY_SLUG = {
    "ceremonial-matcha": {
        "name_th": "มัทฉะเกรด Ceremonial",
        "name_en": "Ceremonial Grade Matcha",
        "description_th": "มัทฉะเกรด Ceremonial organic — 30g",
        "description_en": "Organic ceremonial grade matcha — 30g",
    },
    "matcha-ceremonial": {
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
    "matcha-iced": {
        "name_th": "มัทฉะเย็น",
        "name_en": "Iced Matcha",
        "description_th": "มัทฉะเย็นเข้มข้น หอมสดชื่น",
        "description_en": "Rich, refreshing iced matcha",
    },
    "matcha-culinary-premium": {
        "name_th": "มัทฉะเกรด Culinary พรีเมียม",
        "name_en": "Culinary Grade Premium Matcha",
        "description_th": "มัทฉะเกรด Culinary สำหรับขนมและเครื่องดื่ม",
        "description_en": "Premium culinary grade matcha for baking and drinks",
    },
    "matcha-latte-blend": {
        "name_th": "มัทฉะลาเต้ Blend",
        "name_en": "Matcha Latte Blend",
        "description_th": "สูตรมัทฉะลาเต้ หอมนุ่ม",
        "description_en": "Smooth blend crafted for matcha lattes",
    },
    "hojicha-powder": {
        "name_th": "ผงโฮจิชา",
        "name_en": "Hojicha Powder",
        "description_th": "ชาโฮจิชาคั่ว กลิ่นหอม",
        "description_en": "Roasted hojicha powder with a warm aroma",
    },
    "chasen-whisk": {
        "name_th": "ชาเซ็น (ไม้ไผ่ 80 แฉก)",
        "name_en": "Bamboo Whisk (80 prongs)",
        "description_th": "ที่ตีมัทฉะไม้ไผ่แท้",
        "description_en": "Traditional bamboo matcha whisk",
    },
    "chawan-bowl": {
        "name_th": "ชawan (ถ้วยชงมัทฉะ)",
        "name_en": "Matcha Bowl (Chawan)",
        "description_th": "ถ้วยชงมัทฉะสไตล์ญี่ปุ่น",
        "description_en": "Japanese-style bowl for preparing matcha",
    },
}

CATEGORY_BY_SLUG = {
    "matcha-powder": ("ผงมัทฉะ", "Matcha powder"),
    "matcha-latte": ("มัทฉะลาเต้", "Matcha latte"),
    "matcha-drinks": ("เครื่องดื่มมัทฉะ", "Matcha drinks"),
    "equipment": ("อุปกรณ์", "Tools & accessories"),
}

VARIANT_BY_SKU = {
    "MATCHA-CER-30": ("30 กรัม", "30 g"),
    "MATCHA-CER-50": ("50 กรัม", "50 g"),
    "MATCHA-CUL-100": ("100 กรัม", "100 g"),
    "MATCHA-LAT-30": ("30 กรัม", "30 g"),
    "MATCHA-ICE-30": ("30 กรัม", "30 g"),
    "HOJICHA-50": ("50 กรัม", "50 g"),
    "TOOL-CHASEN": ("1 ชิ้น", "1 pc"),
    "TOOL-CHAWAN": ("1 ชิ้น", "1 pc"),
    "CAP-EX-10": ("Excellent Rich ×10", "Excellent Rich ×10"),
    "CAP-MD-10": ("Medium Rich ×10", "Medium Rich ×10"),
    "CAP-CL-10": ("Classic Rich ×10", "Classic Rich ×10"),
    "GENMAICHA-80": ("80 กรัม", "80 g"),
    "SET-STARTER": ("1 ชุด", "1 set"),
    "RICH-100": ("100 กรัม", "100 g"),
    "RICH-200": ("200 กรัม", "200 g"),
}


def _is_iced_matcha(name, slug):
    lower = name.lower()
    return (
        LAO_ICED in name
        or LAO_COLD in name
        or "iced" in slug
        or "ice" in slug
        or "iced" in lower
    )


def _apply_product_patterns(product):
    name = product.name or ""
    slug = (product.slug or "").lower()
    lower = name.lower()

    if "ceremonial" in lower or "ceremonial" in slug:
        return {
            "name_th": "มัทฉะเกรด Ceremonial",
            "name_en": "Ceremonial Grade Matcha",
        }
    if "culinary" in lower or "culinary" in slug:
        return {
            "name_th": "มัทฉะเกรด Culinary พรีเมียม",
            "name_en": "Culinary Grade Premium Matcha",
        }
    if _is_iced_matcha(name, slug):
        return {
            "name_th": "มัทฉะเย็น",
            "name_en": "Iced Matcha",
            "description_th": "มัทฉะเย็นเข้มข้น หอมสดชื่น",
            "description_en": "Rich, refreshing iced matcha",
        }
    if "latte" in lower or "latte" in slug or LAO_LATTE in name:
        return {
            "name_th": "มัทฉะลาเต้ Blend",
            "name_en": "Matcha Latte Blend",
        }
    if "hojicha" in lower or "hojicha" in slug or LAO_HOJICHA in name:
        return {
            "name_th": "ผงโฮจิชา",
            "name_en": "Hojicha Powder",
        }
    if "chasen" in slug or "whisk" in slug or LAO_CHASEN in name:
        return {
            "name_th": "ชาเซ็น (ไม้ไผ่ 80 แฉก)",
            "name_en": "Bamboo Whisk (80 prongs)",
        }
    if "chawan" in slug or "bowl" in slug or LAO_CHAWAN in name:
        return {
            "name_th": "ชawan (ถ้วยชงมัทฉะ)",
            "name_en": "Matcha Bowl (Chawan)",
        }
    return None


def _apply_category_patterns(category):
    name = category.name or ""
    slug = (category.slug or "").lower()

    if slug in CATEGORY_BY_SLUG:
        return CATEGORY_BY_SLUG[slug]
    if "ຜົງ" in name or "powder" in slug:
        return ("ผงมัทฉะ", "Matcha powder")
    if LAO_LATTE in name or "latte" in slug:
        return ("มัทฉะลาเต้", "Matcha latte")
    if "ອຸປ" in name or "equipment" in slug or "tool" in slug:
        return ("อุปกรณ์", "Tools & accessories")
    if name in LAO_MATCHA_CAT or slug in ("matcha", "matcha-drinks"):
        return ("มัทฉะ", "Matcha")
    if LAO_ICED in name and "ຜົງ" not in name:
        return ("มัทฉะ", "Matcha")
    return None


def sync_catalog_i18n(only_missing=True):
    from apps.catalog.models import Category, Product, ProductVariant

    updated = {"categories": 0, "products": 0, "variants": 0}

    for slug, (name_th, name_en) in CATEGORY_BY_SLUG.items():
        qs = Category.objects.filter(slug=slug)
        if only_missing:
            qs = qs.filter(Q(name_th="") | Q(name_en=""))
        updated["categories"] += qs.update(name_th=name_th, name_en=name_en)

    for cat in Category.objects.all():
        if only_missing and cat.name_th and cat.name_en:
            continue
        pair = _apply_category_patterns(cat)
        if not pair:
            continue
        name_th, name_en = pair
        fields = []
        if not cat.name_th or not only_missing:
            cat.name_th = name_th
            fields.append("name_th")
        if not cat.name_en or not only_missing:
            cat.name_en = name_en
            fields.append("name_en")
        if fields:
            cat.save(update_fields=fields)
            updated["categories"] += 1

    for slug, data in PRODUCT_BY_SLUG.items():
        qs = Product.objects.filter(slug=slug)
        if only_missing:
            qs = qs.filter(Q(name_th="") | Q(name_en=""))
        for product in qs:
            changed = []
            for key, val in data.items():
                if val and (not only_missing or not getattr(product, key)):
                    setattr(product, key, val)
                    changed.append(key)
            if changed:
                product.save(update_fields=changed)
                updated["products"] += 1

    for product in Product.objects.all():
        if only_missing and product.name_th and product.name_en:
            continue
        data = _apply_product_patterns(product)
        if not data:
            continue
        fields = []
        for key, val in data.items():
            if val and (not only_missing or not getattr(product, key)):
                setattr(product, key, val)
                fields.append(key)
        if fields:
            product.save(update_fields=fields)
            updated["products"] += 1

    for sku, (name_th, name_en) in VARIANT_BY_SKU.items():
        qs = ProductVariant.objects.filter(sku=sku)
        if only_missing:
            qs = qs.filter(Q(display_name_th="") | Q(display_name_en=""))
        updated["variants"] += qs.update(display_name_th=name_th, display_name_en=name_en)

    for variant in ProductVariant.objects.all():
        if only_missing and variant.display_name_th and variant.display_name_en:
            continue
        dn = variant.display_name or ""
        if "100" in dn:
            variant.display_name_th = variant.display_name_th or "100 กรัม"
            variant.display_name_en = variant.display_name_en or "100 g"
        elif "50" in dn:
            variant.display_name_th = variant.display_name_th or "50 กรัม"
            variant.display_name_en = variant.display_name_en or "50 g"
        elif "30" in dn or LAO_GRAM in dn:
            variant.display_name_th = variant.display_name_th or "30 กรัม"
            variant.display_name_en = variant.display_name_en or "30 g"
        else:
            continue
        variant.save(update_fields=["display_name_th", "display_name_en"])
        updated["variants"] += 1

    return updated
