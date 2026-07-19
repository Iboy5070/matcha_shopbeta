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
    name = models.CharField("Cas_Name", max_length=100, unique=True)
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

    class Meta:
        verbose_name = "ໝວດໝູ່ (Category)"
        verbose_name_plural = "ໝວດໝູ່ (Categories)"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="Cas_ID")
    name = models.CharField("Pro_Name", max_length=200)
    name_th = models.CharField("ชื่อ (ไทย)", max_length=200, blank=True)
    name_en = models.CharField("Name (EN)", max_length=200, blank=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField("Description", blank=True)
    description_th = models.TextField("คำอธิบาย (ไทย)", blank=True)
    description_en = models.TextField("Description (EN)", blank=True)
    
    price = models.DecimalField("Price", max_digits=12, decimal_places=2, default=0)
    stock_qty = models.PositiveIntegerField(
        "Stock_qty (impl.)",
        default=0,
        help_text="ເພີ່ມຕອນ implement — ຈຳນວນພ້ອມຂาย (ບົດບໍ່ມີ)",
    )
    image = models.ImageField("Img_path (upload)", upload_to="products/", blank=True)
    image_url = models.URLField(
        "Img_path (URL)",
        blank=True,
        help_text="ບົດ: Img_path — ລິ້ງຮູບ CDN/Supabase",
    )
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField("Created_at", auto_now_add=True)

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

    class Meta:
        verbose_name = "ສິນຄ້າ (Product)"
        verbose_name_plural = "ສິນຄ້າ (Products)"

    def __str__(self):
        return self.name
