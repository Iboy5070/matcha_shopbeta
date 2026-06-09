from django.http import HttpResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD", "OPTIONS"])
def healthz(request):
    if request.method == "OPTIONS":
        response = HttpResponse()
    else:
        response = HttpResponse("ok", content_type="text/plain")
    response["Cache-Control"] = "no-store"
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
    return response
