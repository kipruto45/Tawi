from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import GeneratedReport


@receiver(post_delete, sender=GeneratedReport)
def delete_report_file(sender, instance, **kwargs):
    """Remove generated report file from storage when GeneratedReport is deleted."""
    try:
        if getattr(instance, 'file', None) and hasattr(instance.file, 'storage'):
            instance.file.delete(save=False)
    except Exception:
        pass
