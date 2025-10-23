from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from trees.models import Tree
from beneficiaries.models import PlantingSite, Beneficiary
from monitoring.models import FollowUp


def _clear_dashboard_cache_for_all():
    # Invalidate any keys that start with dashboard_summary (simple approach)
    # In production, keep a list of keys or use a cache tagging library.
    for key in list(cache._cache.keys()) if hasattr(cache, '_cache') else []:
        if str(key).startswith('dashboard'):
            try:
                cache.delete(key)
            except Exception:
                pass


@receiver(post_save, sender=Tree)
@receiver(post_delete, sender=Tree)
def tree_changed(sender, instance, **kwargs):
    _clear_dashboard_cache_for_all()


@receiver(post_save, sender=PlantingSite)
@receiver(post_delete, sender=PlantingSite)
def site_changed(sender, instance, **kwargs):
    _clear_dashboard_cache_for_all()


@receiver(post_save, sender=Beneficiary)
@receiver(post_delete, sender=Beneficiary)
def beneficiary_changed(sender, instance, **kwargs):
    _clear_dashboard_cache_for_all()


@receiver(post_save, sender=FollowUp)
@receiver(post_delete, sender=FollowUp)
def followup_changed(sender, instance, **kwargs):
    _clear_dashboard_cache_for_all()
