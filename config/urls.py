from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from config.health import healthz

urlpatterns = [
    path("healthz/", healthz),
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("apps.store.urls")),
    path("", include("apps.sales.urls")),
]

# serve uploaded images (admin uploads → /media/products/...)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
