import uuid
from io import BytesIO
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.files.base import ContentFile

import qrcode


def qrcode_upload_to(instance, filename):
    return f'qrcodes/{instance.pk or "new"}/{filename}'


class QRCode(models.Model):
    """Represents a QR code linked to a Tree or PlantingSite.

    The QR encodes a URL path in the app that can be scanned publicly.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tree = models.ForeignKey('trees.Tree', null=True, blank=True, on_delete=models.SET_NULL)
    site = models.ForeignKey('beneficiaries.PlantingSite', null=True, blank=True, on_delete=models.SET_NULL)
    label = models.CharField(max_length=128, blank=True)
    image = models.ImageField(upload_to=qrcode_upload_to, null=True, blank=True)
    scan_count = models.PositiveIntegerField(default=0)
    last_scanned = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_scan_path(self):
        # public scan endpoint (relative)
        return reverse('qrcode-scan', kwargs={'pk': str(self.pk)})

    def get_absolute_url(self):
        return reverse('qrcodes-detail', kwargs={'pk': str(self.pk)})

    def generate_image(self, base_url=None):
        """Generate and save a QR image pointing to the scan URL."""
        if base_url is None:
            base_url = getattr(settings, 'SITE_BASE_URL', '')
        target = (base_url.rstrip('/') if base_url else '') + self.get_scan_path()
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(target)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        name = f'{self.pk}.png'
        self.image.save(name, ContentFile(bio.read()), save=False)
        bio.close()
        return self.image

    def increment_scan(self, when):
        self.scan_count = models.F('scan_count') + 1
        self.last_scanned = when
        self.save(update_fields=['scan_count','last_scanned'])

    def __str__(self):
        return f'QR {self.label or self.pk}'
