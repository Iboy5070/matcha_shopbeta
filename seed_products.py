import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.catalog.models import Category, Product

# Clear old data
Category.objects.all().delete()
Product.objects.all().delete()

# Create Categories
matcha_cat = Category.objects.create(name="Matcha", name_th="ມັດຊະ", name_en="Matcha", slug="matcha")
tea_cat = Category.objects.create(name="Tea", name_th="ຊາ", name_en="Tea", slug="tea")
equip_cat = Category.objects.create(name="Equipment", name_th="ອຸປະກອນ", name_en="Equipment", slug="equipment")

# Create Products
products = [
    {
        "category": matcha_cat,
        "name": "Ceremonial Grade Matcha",
        "description": "Premium matcha from Uji, Kyoto.",
        "price": 250000.00,
        "slug": "ceremonial-matcha",
        "image_url": "/static/img/products/matcha-ceremonial-50g.jpg",
        "is_active": True,
        "is_featured": True
    },
    {
        "category": matcha_cat,
        "name": "Culinary Grade Matcha",
        "description": "Perfect for baking and lattes.",
        "price": 120000.00,
        "slug": "culinary-matcha",
        "image_url": "/static/img/products/matcha-premium-30g.jpg",
        "is_active": True,
        "is_featured": False
    },
    {
        "category": tea_cat,
        "name": "Houjicha Roasted Tea",
        "description": "Low caffeine roasted green tea.",
        "price": 150000.00,
        "slug": "houjicha",
        "image_url": "/static/img/products/matcha-classic-100g.jpg",
        "is_active": True,
        "is_featured": True
    },
    {
        "category": equip_cat,
        "name": "Bamboo Whisk (Chasen)",
        "description": "Traditional tool for whisking matcha.",
        "price": 85000.00,
        "slug": "bamboo-whisk",
        "image_url": "/static/img/products/bamboo-whisk-chasen.jpg",
        "is_active": True,
        "is_featured": True
    }
]

for p_data in products:
    Product.objects.create(**p_data)

print(f"Successfully seeded {len(products)} products in {Category.objects.count()} categories!")
