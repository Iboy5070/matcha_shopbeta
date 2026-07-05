from django.contrib.auth import authenticate, get_user_model


def authenticate_by_identifier(request, identifier: str, password: str):
    """Login with username or email (shop modal + team accounts)."""
    identifier = (identifier or "").strip()
    password = password or ""
    if not identifier or not password:
        return None

    user = authenticate(request, username=identifier, password=password)
    if user is not None:
        return user

    User = get_user_model()
    if "@" in identifier:
        match = User.objects.filter(email__iexact=identifier).first()
        if match:
            return authenticate(request, username=match.username, password=password)
    return None
