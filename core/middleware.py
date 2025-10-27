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
        # Ensure authenticated users have a Profile to avoid template-level
        # RelatedObjectDoesNotExist errors when templates access
        # `request.user.profile`. This is a lightweight, best-effort
        # approach: attempt to create the Profile if missing and swallow
        # any errors to avoid breaking request handling.
        try:
            if getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
                # Local import to avoid app-loading issues at module import time.
                try:
                    from accounts.models import Profile
                    # get_or_create is idempotent and safe in concurrent runs here
                    Profile.objects.get_or_create(user=request.user)
                except Exception:
                    # If anything goes wrong creating a profile, don't fail the
                    # request — templates will continue to handle missing values.
                    pass
        except Exception:
            # Swallow any unexpected errors in middleware to avoid 500s
            # originating here.
            pass
        return self.get_response(request)
