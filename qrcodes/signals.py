from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import QRCode


@receiver(post_delete, sender=QRCode)
def delete_qrcode_image(sender, instance, **kwargs):
    """Remove the QRCode.image file from storage when a QRCode is deleted."""
    try:
        if instance.image:
            instance.image.delete(save=False)
    except Exception:
        pass
