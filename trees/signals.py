from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Tree


@receiver(post_delete, sender=Tree)
def delete_tree_qr_image(sender, instance, **kwargs):
    """Remove the Tree.qr_image file from storage when a Tree is deleted."""
    try:
        if instance.qr_image:
            instance.qr_image.delete(save=False)
    except Exception:
        pass
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tree


@receiver(post_save, sender=Tree)
def ensure_qrcode_for_tree(sender, instance, created, **kwargs):
    """Ensure a QRCode record exists for each Tree and generate its image.

    This runs after a Tree is saved. If no QRCode exists linking to this
    Tree, create one and generate the PNG image using the QRCode model's
    helper. This keeps a canonical QRCode record separate from the
    Tree.qr_image ImageField which is intended as a simple inline image.
    """
    try:
        # avoid importing at module import time to reduce startup coupling
        from qrcodes.models import QRCode
    except Exception:
        return

    try:
        # if there is already a QRCode for this tree, ensure it has an image
        q = QRCode.objects.filter(tree=instance).first()
        if q is None:
            q = QRCode.objects.create(tree=instance, label=str(instance.tree_id))
        # generate image if missing
        if not q.image:
            q.generate_image()
            q.save(update_fields=['image'])
    except Exception:
        # don't let QR failures break tree saves
        return
