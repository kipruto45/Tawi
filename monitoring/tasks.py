from celery import shared_task
from django.utils import timezone
from .models import MonitoringReport, FollowUp


@shared_task
def check_low_survival_and_alert(threshold=60.0):
    """Find recent monitoring reports with survival below threshold and produce alerts (stub)."""
    now = timezone.now().date()
    low = MonitoringReport.objects.filter(total_planted__gt=0).annotate().filter(( ( 'surviving' ), ) )[:100]
    # This is intentionally a stub — integrate with notifications/email in production
    return {'checked': now.isoformat(), 'found': low.count()}


@shared_task
def notify_overdue_followups():
    today = timezone.now().date()
    overdue = FollowUp.objects.filter(scheduled_date__lt=today, completed=False)
    return {'overdue_count': overdue.count()}
