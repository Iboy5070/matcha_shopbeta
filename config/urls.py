from django.contrib import admin
from django.urls import path, include, re_path
import config.admin_branding  # noqa: F401 — ຫົວ Admin MATCHAZUKI
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as media_serve
from django.views.i18n import set_language
from config.health import healthz
from config.sitemap import robots_txt, sitemap_xml

urlpatterns = [
    path("healthz", healthz),
    path("healthz/", healthz),
    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("", include("apps.store.urls")),
    path("", include("apps.sales.urls")),
]

# Local dev: Django helper. Production: explicit serve (static() is no-op when DEBUG=False).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            media_serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
handler403 = "config.views_errors.permission_denied"
handler404 = "config.views_errors.page_not_found"
handler500 = "config.views_errors.server_error"
