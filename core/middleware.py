from django.contrib.auth.models import AnonymousUser


class EnsureUserMiddleware:
    """Lightweight middleware that ensures `request.user` exists.

    This guards template rendering and context processors against environments
    where AuthenticationMiddleware is missing or misordered. If the real
    AuthenticationMiddleware runs later it will overwrite this attribute.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user'):
            request.user = AnonymousUser()
        return self.get_response(request)
