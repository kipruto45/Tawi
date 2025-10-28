from notifications.models import Notification
from django.db import OperationalError


def notifications_context(request):
  """Provide unread notification count and a short preview list for the header dropdown.

  This processor is defensive: some request objects (test RequestFactory or
  misconfigured middleware) may not have a `user` attribute. In that case
  return an empty notification context rather than raising an exception
  which would cause a 500 error site-wide.

  Returns:
    - unread_notifications_count: int
    - notifications_preview: list of latest 5 notifications for the user
  """
  user = getattr(request, 'user', None)
  if not user or not getattr(user, 'is_authenticated', False):
    return {'unread_notifications_count': 0, 'notifications_preview': []}

  try:
    qs = Notification.objects.filter(recipient=user).order_by('-created_at')
    count = qs.filter(unread=True).count()
    preview = list(qs[:5])
  except OperationalError:
    # In development the database schema can be out-of-sync (missing columns).
    # Fail gracefully: show no notifications rather than crashing the page.
    count = 0
    preview = []

  return {'unread_notifications_count': count, 'notifications_preview': preview}


def user_profile(request):
  """Expose a safe `user_profile` variable to templates.

  Returns a dict with 'user_profile' set to the user's profile object when
  available, otherwise None. This prevents templates from raising when they
  try to access `request.user.profile` for AnonymousUser or when the profile
  relation is not yet created.
  """
  user = getattr(request, 'user', None)
  if not user or not getattr(user, 'is_authenticated', False):
    return {'user_profile': None}

  try:
    profile = getattr(user, 'profile', None)
  except Exception:
    profile = None

  return {'user_profile': profile}


def admin_flag(request):
  """Expose a simple `is_admin` boolean to templates for consistent checks.

  This prefers explicit permission `dashboard.view_admin_dashboard` or
  the `Admins` group as a fallback to the legacy `is_staff`/role checks.
  """
  user = getattr(request, 'user', None)
  try:
    if not user or not getattr(user, 'is_authenticated', False):
      return {'is_admin': False}
    # prefer permission-based check
    if user.has_perm('dashboard.view_admin_dashboard'):
      return {'is_admin': True}
    # fallback to group membership
    groups = set(user.groups.values_list('name', flat=True))
    if 'Admins' in groups:
      return {'is_admin': True}
    return {'is_admin': False}
  except Exception:
    return {'is_admin': False}
