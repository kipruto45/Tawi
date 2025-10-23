"""Background tasks for dashboard analytics.

This file contains lightweight placeholders. Integrate Celery + Redis in production and
register periodic tasks in Celery beat.
"""
from celery import shared_task


@shared_task
def recompute_dashboard_aggregates():
    """Placeholder task that would recompute and warm caches for dashboard metrics."""
    # Example: call service and store in cache
    try:
        from .services.dashboard_service import get_dashboard_summary
        from django.core.cache import cache
        data = get_dashboard_summary()
        cache.set('dashboard_summary_background', data, 60 * 60)
    except Exception:
        # in real task log the exception
        pass
