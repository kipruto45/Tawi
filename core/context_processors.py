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
