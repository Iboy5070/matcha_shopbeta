from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product = ຊື່ຫຼັກ: "Matcha Premium", "Matcha Latte", "Whisk" ...
    Variant = ຕົວທີ່ຂາຍຈິງ: 50g/100g ຫຼື Hot/Ice + S/M/L
    """
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    class Temperature(models.TextChoices):
        HOT = "HOT", "Hot"
        ICE = "ICE", "Ice"

    class Size(models.TextChoices):
        S = "S", "S"
        M = "M", "M"
        L = "L", "L"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # ຕົວທີ່ສຳຄັນສຸດ (ຫ້າມຊ້ຳ)
    sku = models.CharField(max_length=50, unique=True)

    # ໃຊ້ສະແດງ: "50g", "100g", "Hot M", "Ice L"
    display_name = models.CharField(max_length=120)

    # ---- ສຳລັບແບບ 50g/100g ----
    weight_g = models.PositiveIntegerField(null=True, blank=True)  # 50,100,...

    # ---- ສຳລັບ drink menu ----
    temperature = models.CharField(max_length=3, choices=Temperature.choices, null=True, blank=True)
    size = models.CharField(max_length=1, choices=Size.choices, null=True, blank=True)

    unit = models.CharField(max_length=20, default="pcs")  # pcs, bag, g, cup
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    stock_qty = models.IntegerField(default=0)           # stock ຢູ່ variant
    reorder_level = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        (optional) ເບື້ອງຕົ້ນ: ບໍ່ບັງຄັບເຂັ້ມ ເພາະເຈົ້າຢາກຮອງຮັບທັງ 2 ແບບ
        ແຕ່ຖ້າຈະບັງຄັບ ຄ່ອຍເພີ່ມ validation ພາຍຫຼັງ
        """
        super().clean()

    def __str__(self):
        return f"{self.product.name} - {self.display_name}"
