from django.db import models
from django.utils.text import slugify


def _pick_lang(lang, lo, th="", en=""):
    if lang == "en" and en:
        return en
    if lang == "th" and th:
        return th
    if lang == "lo" and lo:
        return lo
    return lo or th or en


class Category(models.Model):
    name = models.CharField("ຊື່ (ລາວ)", max_length=100, unique=True)
    name_th = models.CharField("ชื่อ (ไทย)", max_length=100, blank=True)
    name_en = models.CharField("Name (EN)", max_length=100, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def name_for(self, lang):
        return _pick_lang(lang, self.name, self.name_th, self.name_en)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or f"cat-{self.name[:20]}"
            if not base or not base.replace("-", ""):
                base = f"category-{abs(hash(self.name)) % 10000}"
            slug = base
            n = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField("ຊື່ (ລາວ)", max_length=200)
    name_th = models.CharField("ชื่อ (ไทย)", max_length=200, blank=True)
    name_en = models.CharField("Name (EN)", max_length=200, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField("ຄຳອະທິບາຍ (ລາວ)", blank=True)
    description_th = models.TextField("คำอธิบาย (ไทย)", blank=True)
    description_en = models.TextField("Description (EN)", blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    image_url = models.URLField(
        blank=True,
        help_text="ລິ້ງຮູບຈາກ CDN (ແນະນຳສຳລັບ production — ບໍ່ຫາຍເມື່ອ deploy)",
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def name_for(self, lang):
        return _pick_lang(lang, self.name, self.name_th, self.name_en)

    def description_for(self, lang):
        return _pick_lang(lang, self.description, self.description_th, self.description_en)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "product"
            slug = base
            n = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def display_image(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return ""

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
    sku = models.CharField(max_length=50, unique=True)
    display_name = models.CharField("ຊື່ສະແດງ (ລາວ)", max_length=120)
    display_name_th = models.CharField("ชื่อ (ไทย)", max_length=120, blank=True)
    display_name_en = models.CharField("Name (EN)", max_length=120, blank=True)
    weight_g = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.CharField(max_length=3, choices=Temperature.choices, null=True, blank=True)
    size = models.CharField(max_length=1, choices=Size.choices, null=True, blank=True)
    unit = models.CharField(max_length=20, default="pcs")
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_qty = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def display_name_for(self, lang):
        return _pick_lang(lang, self.display_name, self.display_name_th, self.display_name_en)

    def clean(self):
        super().clean()

    def __str__(self):
        return f"{self.product.name} - {self.display_name}"
