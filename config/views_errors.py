from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, "errors/404.html", status=404)


def permission_denied(request, exception):
    staff_limited = (
        request.user.is_authenticated
        and request.user.is_staff
        and not request.user.is_superuser
    )
    return render(
        request,
        "errors/403.html",
        {"staff_limited": staff_limited},
        status=403,
    )


def server_error(request):
    return render(request, "errors/500.html", status=500)
