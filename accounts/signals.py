from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Profile


@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    """Remove profile picture file from storage when Profile is deleted."""
    try:
        f = instance.profile_picture
        if f and hasattr(f, 'storage'):
            f.delete(save=False)
    except Exception:
        pass
