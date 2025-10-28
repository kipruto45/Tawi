from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Media


@receiver(post_delete, sender=Media)
def delete_media_files(sender, instance, **kwargs):
    """Remove uploaded media files and thumbnails when a Media instance is deleted."""
    try:
        if getattr(instance, 'file', None) and hasattr(instance.file, 'storage'):
            instance.file.delete(save=False)
    except Exception:
        pass
    try:
        if getattr(instance, 'thumbnail', None) and hasattr(instance.thumbnail, 'storage'):
            instance.thumbnail.delete(save=False)
    except Exception:
        pass
