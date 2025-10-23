from celery import shared_task
from django.utils import timezone
from .models import Tree, TreeUpdate
from django.core.mail import send_mail
from notifications.models import Notification


@shared_task
def remind_missing_updates(days_without=30):
    cutoff = timezone.now().date() - timezone.timedelta(days=days_without)
    trees = Tree.objects.filter(updates__date__lt=cutoff).distinct()
    # create notifications for each tree owner/beneficiary contact if available
    created = 0
    for t in trees:
        # simplistic: notify the beneficiary user if they are a user (assuming Beneficiary has user relation)
        recipient = None
        try:
            recipient = getattr(t.beneficiary, 'user', None)
        except Exception:
            recipient = None
        if recipient:
            Notification.objects.create(recipient=recipient, verb='missing_update', description=f'Tree {t.tree_id} has not been updated for {days_without} days', metadata={'tree': str(t.pk)})
            created += 1
    return {'count': trees.count(), 'notifications_created': created}
