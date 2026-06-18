from django.conf import settings
from django.contrib import admin

admin.site.site_header = f"{settings.SHOP_BRAND} — ຈັດການຮ້ານ"
admin.site.site_title = f"{settings.SHOP_BRAND} Admin"
