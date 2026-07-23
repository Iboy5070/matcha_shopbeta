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
    name = models.CharField(
        "ຊື່ໝວດ (ລາວ)",
        max_length=100,
        unique=True,
        help_text="ຊື່ຫຼັກທີ່ລູກຄ້າເຫັນເມື່ອເລືອກພາສາລາວ",
    )
    name_th = models.CharField("ຊື່ໝວດ (ไทย)", max_length=100, blank=True, help_text="ປ່ອຍວ່າງໄດ້ຖ້າບໍ່ໃຊ້ພາສາໄທ")
    name_en = models.CharField("ຊື່ໝວດ (EN)", max_length=100, blank=True, help_text="ປ່ອຍວ່າງໄດ້ຖ້າບໍ່ໃຊ້ພາສາອັງກິດ")
    slug = models.SlugField(
        "ລະຫັດ URL",
        max_length=120,
        unique=True,
        blank=True,
        help_text="ໃຊ້ໃນ URL ເຊັ່ນ /shop/?category=matcha — ປ່ອຍວ່າງລະບົບຈະສ້າງໃຫ້",
    )

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
        verbose_name = "ໝວດໝູ່ສິນຄ້າ"
        verbose_name_plural = "ໝວດໝູ່ສິນຄ້າ"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="ໝວດໝູ່",
        help_text="ເລືອກໝວດທີ່ສິນຄ້ານີ້ຢູ່",
    )
    name = models.CharField("ຊື່ສິນຄ້າ (ລາວ)", max_length=200, help_text="ຊື່ທີ່ສະແດງໃນໜ້າຮ້ານ")
    name_th = models.CharField("ຊື່ສິນຄ້າ (ไทย)", max_length=200, blank=True)
    name_en = models.CharField("ຊື່ສິນຄ້າ (EN)", max_length=200, blank=True)
    slug = models.SlugField(
        "ລະຫັດ URL",
        max_length=220,
        unique=True,
        blank=True,
        help_text="ປ່ອຍວ່າງໄດ້ — ລະບົບຈະສ້າງອັດຕະໂນມັດ",
    )
    description = models.TextField("ລາຍລະອຽດ (ລາວ)", blank=True, help_text="ອະທິບາຍສັ້ນໆໃຫ້ລູກຄ້າອ່ານ")
    description_th = models.TextField("ລາຍລະອຽດ (ไทย)", blank=True)
    description_en = models.TextField("ລາຍລະອຽດ (EN)", blank=True)

    price = models.DecimalField(
        "ລາຄາ (ກີບ)",
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="ລາຄາຂາຍເປັນກີບລາວ — ຕົວຢ່າງ 120000",
    )
    stock_qty = models.PositiveIntegerField(
        "ຈຳນວນຄົງເຫຼືອ",
        default=0,
        help_text="ຈຳນວນທີ່ຂາຍໄດ້ດຽວນີ້. ຖ້າ = 0 ລູກຄ້າຈະເຫັນ 'ໝົດ — ຈອງໄດ້'",
    )
    image = models.ImageField(
        "ຮູບສິນຄ້າ (ອັບໂຫຼດ)",
        upload_to="products/",
        blank=True,
        help_text="ອັບໂຫຼດຈາກເຄື່ອງ — ໃນ production ແນະນຳໃຊ້ລິ້ງ URL ຂ້າງລຸ່ມ",
    )
    image_url = models.URLField(
        "ລິ້ງຮູບ (URL)",
        blank=True,
        help_text="ວາງລິ້ງຮູບຈາກ CDN/Supabase — ບໍ່ຫາຍເມື່ອ redeploy",
    )
    is_featured = models.BooleanField(
        "ແນະນຳໜ້າຫຼັກ",
        default=False,
        help_text="ຕິກເພື່ອໃຫ້ສິນຄ້າຂຶ້ນໜ້າທຳອິດຂອງຮ້ານ",
    )
    is_active = models.BooleanField(
        "ເປີດຂາຍ",
        default=True,
        help_text="ປິດ = ລູກຄ້າບໍ່ເຫັນສິນຄ້ານີ້ໃນຮ້ານ",
    )
    created_at = models.DateTimeField("ວັນທີສ້າງ", auto_now_add=True)

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
        verbose_name = "ສິນຄ້າ"
        verbose_name_plural = "ສິນຄ້າ"

    def __str__(self):
        return self.name
