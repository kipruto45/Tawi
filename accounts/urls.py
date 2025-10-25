from django.urls import path
from .views import CustomLoginView
from .views import register, profile_view, profile_edit_view, user_list, user_detail
from .views import role_management, guest_dashboard
from .views import api_register, api_profile
from .views import api_role_check, api_change_role
from .views import post_login_redirect
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    path('register/', register, name='register'),
    # Convenience alias used by templates that link to an "add user" page.
    # Map to the existing `register` view so template reverses succeed.
    path('add/', register, name='add_user'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('users/', user_list, name='user_list'),
    path('users/<int:pk>/', user_detail, name='user_detail'),
    # Templates sometimes link to role-edit/delete pages per-user. There is no
    # full-featured edit/delete view in this codebase yet, so expose safe
    # named URLs that reverse correctly and render the existing user_detail
    # page when visited. These act as low-risk placeholders until real
    # management views are implemented.
    path('users/<int:pk>/role-edit/', user_detail, name='role_edit'),
    path('users/<int:pk>/role-delete/', user_detail, name='role_delete'),
    path('roles/', role_management, name='role_management'),
    path('guest/', guest_dashboard, name='guest_dashboard'),
    path('volunteer-signup/', register, name='volunteer_sign_up'),
    # API
    path('api/register/', api_register, name='api_register'),
    path('api/profile/', api_profile, name='api_profile'),
    path('api/role_check/', api_role_check, name='api_role_check'),
    path('api/change_role/', api_change_role, name='api_change_role'),
    path('post-login/', post_login_redirect, name='post_login_redirect'),
]

# If django-two-factor-auth is installed and USE_2FA is enabled, the
# two_factor package exposes an alternate login flow at /account/login/ and
# related setup endpoints. We purposely do NOT replace the existing
# `accounts:login` route here to avoid surprising changes to URL resolution
# (many tests and templates rely on the non-2FA login behavior). To enable
# the two-factor login flow, users can visit the namespaced two_factor URL
# (mounted under /account/). Keeping the default `accounts:login` mapping
# stable prevents the ManagementForm tampering errors in tests that perform
# direct POSTs to the login view.

# Define the application namespace so reversing 'accounts:...' works reliably
app_name = 'accounts'

# If django-allauth is installed and enabled, include its URLs so provider login
# flows (e.g. Google) are available at /accounts/social/.
try:
    import allauth
    from django.urls import include
    urlpatterns += [
        path('social/', include('allauth.socialaccount.urls')),
        # Ensure provider-specific URLs are available at /accounts/<provider>/
        # (some setups register provider URLs differently; include explicitly to be robust)
    path('', include('allauth.urls')),
    # Explicitly mount the Google provider URLs at /accounts/google/ so the
    # callback endpoint (/accounts/google/login/callback/) is present and
    # won't return a 404 during the OAuth flow.
    path('google/', include('allauth.socialaccount.providers.google.urls')),
    ]
except Exception:
    # allauth not installed in this environment; skip provider URL wiring.
    pass
