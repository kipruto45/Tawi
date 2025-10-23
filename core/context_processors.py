from notifications.models import Notification
from django.db import OperationalError


def notifications_context(request):
  """Provide unread notification count and a short preview list for the header dropdown.

  Returns:
    - unread_notifications_count: int
    - notifications_preview: list of latest 5 notifications for the user
  """
  if not request.user.is_authenticated:
    return {'unread_notifications_count': 0, 'notifications_preview': []}

  try:
    qs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    count = qs.filter(unread=True).count()
    preview = list(qs[:5])
  except OperationalError:
    # In development the database schema can be out-of-sync (missing columns).
    # Fail gracefully: show no notifications rather than crashing the page.
    count = 0
    preview = []

  return {'unread_notifications_count': count, 'notifications_preview': preview}
