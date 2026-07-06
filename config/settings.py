import os
from pathlib import Path
from dotenv import load_dotenv
from django.urls import reverse_lazy

from config.database import configure_databases

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
DEBUG = os.getenv("DEBUG", "0") == "1"

# ALLOWED_HOSTS: ຮອງຮັບ Railway (.up.railway.app) ແລະ domain ກຳນົດເອງ
_raw_hosts = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]

# Railway inject RAILWAY_STATIC_URL; ຮັບ domain ອັດຕະໂນມັດ
_railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# Render injects RENDER_EXTERNAL_HOSTNAME on deploy
_render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

# Production Render hosts (avoid DisallowedHost if env is misconfigured)
if not DEBUG:
    for _host in ("matcha-shopbeta.onrender.com", ".onrender.com"):
        if _host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_host)

# CSRF — ຕ້ອງລິດ domain production ໄວ້ດ້ວຍ
CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if "." in h
]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.catalog.apps.CatalogConfig",
    "apps.sales.apps.SalesConfig",
    "apps.inventory.apps.InventoryConfig",
    "apps.store.apps.StoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "config.middleware.AdminSuperuserOnlyMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "config.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = configure_databases(BASE_DIR, DEBUG)

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "lo"
LANGUAGES = [
    ("lo", "Lao"),
    ("en", "English"),
    ("th", "Thai"),
]

import django.conf.locale

EXTRA_LANG_INFO = {
    "lo": {
        "bidi": False,
        "code": "lo",
        "name": "Lao",
        "name_local": "ລາວ",
    },
}

django.conf.locale.LANG_INFO.update(EXTRA_LANG_INFO)

LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Vientiane"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")
LINE_URL = os.getenv("LINE_URL", "")
FACEBOOK_URL = os.getenv("FACEBOOK_URL", "")

# WhatsApp: ໃຊ້ WHATSAPP_URL ຫຼື WHATSAPP_PHONE (ເຊັ່ນ 8562012345678)
WHATSAPP_URL = os.getenv("WHATSAPP_URL", "")
if not WHATSAPP_URL:
    _wa_phone = os.getenv("WHATSAPP_PHONE", "").strip().lstrip("+").replace(" ", "").replace("-", "")
    if _wa_phone:
        WHATSAPP_URL = f"https://wa.me/{_wa_phone}"

# ບັນຊີໂອນເງິນ (ສະແດງໃນ Checkout + ໜ້າສຳເລັດສັ່ງຊື່)
BANK_NAME = os.getenv("BANK_NAME", "")
BANK_ACCOUNT_NUMBER = os.getenv("BANK_ACCOUNT_NUMBER", "")
BANK_ACCOUNT_NAME = os.getenv("BANK_ACCOUNT_NAME", "")
# ຮູບ LAO QR ຈາກ BCEL One (screenshot/save ແລ້ວອັບໂຫຼດ CDN)
BANK_QR_IMAGE_URL = os.getenv("BANK_QR_IMAGE_URL", "")

_default_site_url = "http://127.0.0.1:8000" if DEBUG else "https://matcha-shopbeta.onrender.com"
SITE_URL = os.getenv("SITE_URL", _default_site_url).rstrip("/")
SHOP_NAME = os.getenv("SHOP_NAME", "The 196 Haus")
SHOP_TAGLINE = os.getenv("SHOP_TAGLINE", "MATCHA")
SHOP_BRAND = os.getenv("SHOP_BRAND", f"{SHOP_NAME} {SHOP_TAGLINE}")
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/"
CUSTOMER_LOGIN_URL = "store_login"

from django.contrib.messages import constants as message_constants

MESSAGE_TAGS = {
    message_constants.DEBUG: "secondary",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
# ໜ້າ wake ຟຣີ (GitHub Pages) — ແຊຮລິ້ກນີ້ໃນ Facebook/LINE ແທນ Render URL ໂດຍກົງ
WAKE_PAGE_URL = os.getenv("WAKE_PAGE_URL", "https://iboy5070.github.io/matcha_shopbeta/").rstrip("/") + "/"
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", CONTACT_EMAIL)
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN", "")

# Supabase Storage for payment slips (persists across Render redeploys)
DATABASE_URL = os.getenv("DATABASE_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_SLIP_BUCKET = os.getenv("SUPABASE_SLIP_BUCKET", "slips")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@196haus-matcha.local")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
if EMAIL_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
else:
    EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

from django.templatetags.static import static

UNFOLD = {
    "SITE_TITLE": SHOP_NAME,
    "SITE_HEADER": SHOP_NAME,
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("img/icons/logo-cup.png"),
        "dark": lambda request: static("img/icons/logo-cup.png"),
    },
    "COLORS": {
        "primary": {
            "50": "246 250 247",
            "100": "232 243 236",
            "200": "206 229 216",
            "300": "167 207 184",
            "400": "122 178 144",
            "500": "88 149 112",
            "600": "65 119 86",
            "700": "53 96 70",
            "800": "45 78 58",
            "900": "37 64 48",
            "950": "20 37 27",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "ສະຫຼຸບຂໍ້ມູນ (Dashboard)",
                "separator": True,
                "items": [
                    {
                        "title": "ໜ້າຫຼັກ",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "ການຂາຍ (Sales)",
                "separator": True,
                "items": [
                    {
                        "title": "ອໍເດີ (Orders)",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:sales_order_changelist"),
                    },
                    {
                        "title": "ການຊຳລະເງິນ (Payments)",
                        "icon": "payments",
                        "link": reverse_lazy("admin:sales_payment_changelist"),
                    },
                    {
                        "title": "ບິນ (Bills)",
                        "icon": "receipt",
                        "link": reverse_lazy("admin:sales_bill_changelist"),
                    },
                    {
                        "title": "ສິນຄ້າຈອງ (Reserved)",
                        "icon": "bookmark",
                        "link": reverse_lazy("admin:sales_reserved_changelist"),
                    },
                ],
            },
            {
                "title": "ສາງສິນຄ້າ (Inventory)",
                "separator": True,
                "items": [
                    {
                        "title": "ສິນຄ້າໃນສາງ (Stock)",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:inventory_inventory_changelist"),
                    },
                    {
                        "title": "ນຳເຂົ້າ (Imports)",
                        "icon": "local_shipping",
                        "link": reverse_lazy("admin:inventory_imports_changelist"),
                    },
                    {
                        "title": "ໃບສັ່ງຊື້ (Purchase Orders)",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:inventory_purchaseorder_changelist"),
                    },
                    {
                        "title": "ຜູ້ສະໜອງ (Suppliers)",
                        "icon": "storefront",
                        "link": reverse_lazy("admin:inventory_supplier_changelist"),
                    },
                ],
            },
            {
                "title": "ສິນຄ້າ (Catalog)",
                "separator": True,
                "items": [
                    {
                        "title": "ລາຍການສິນຄ້າ",
                        "icon": "category",
                        "link": reverse_lazy("admin:catalog_product_changelist"),
                    },
                    {
                        "title": "ໝວດໝູ່ (Categories)",
                        "icon": "folder",
                        "link": reverse_lazy("admin:catalog_category_changelist"),
                    },
                ],
            },
            {
                "title": "ຜູ້ໃຊ້ (Users)",
                "separator": True,
                "items": [
                    {
                        "title": "ພະນັກງານ (Employees)",
                        "icon": "badge",
                        "link": reverse_lazy("admin:store_employee_changelist"),
                    },
                    {
                        "title": "ລູກຄ້າ (Customers)",
                        "icon": "groups",
                        "link": reverse_lazy("admin:store_customer_changelist"),
                    },
                    {
                        "title": "ແອັດມິນ (Admins)",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
    "STYLES": [
        "/static/css/unfold_custom.css",
    ],
}
