from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse


def robots_txt(_request):
    site = settings.SITE_URL.rstrip("/")
    body = f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def sitemap_xml(_request):
    site = settings.SITE_URL.rstrip("/")
    paths = [
        "store_home",
        "store_shop",
        "store_about",
        "store_faq",
        "store_contact",
        "store_confirm_payment",
        "store_returns",
        "store_privacy",
        "store_blog_list",
    ]
    urls = "\n".join(
        f"  <url><loc>{site}{reverse(name)}</loc></url>"
        for name in paths
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
    return HttpResponse(xml, content_type="application/xml")
