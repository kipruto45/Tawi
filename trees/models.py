from django.db import models
from beneficiaries.models import Beneficiary
from django.conf import settings
import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
try:
    from django.contrib.gis.db import models as geomodels
    HAS_GEODJANGO = True
except Exception:
    geomodels = None
    HAS_GEODJANGO = False


def tree_qr_upload_to(instance, filename):
    return f'trees/qrcodes/{instance.pk or "new"}/{filename}'

class TreeSpecies(models.Model):
    name = models.CharField(max_length=200)
    co2_estimate_kg_per_year = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class TreeCampaign(models.Model):
    name = models.CharField(max_length=200)
    target = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tree(models.Model):
    STATUS_CHOICES = [
        ('alive', 'Alive'),
        ('dead', 'Dead'),
        ('replanted', 'Replanted'),
    ]
    tree_id = models.CharField(max_length=64, unique=True)
    species = models.ForeignKey(TreeSpecies, null=True, blank=True, on_delete=models.SET_NULL)
    planting_date = models.DateField()
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    # optional campaign/event
    campaign = models.ForeignKey('TreeCampaign', null=True, blank=True, on_delete=models.SET_NULL)
    number_of_seedlings = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='alive')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # optional GeoDjango point field (use PostGIS and GeoDjango for production spatial queries)
    if HAS_GEODJANGO:
        location = geomodels.PointField(null=True, blank=True)

    qr_image = models.ImageField(upload_to=tree_qr_upload_to, null=True, blank=True)
    # cause of death when status == dead
    cause_of_death = models.CharField(max_length=128, blank=True)
    # linkage to replacement tree
    replaced_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replacements')
    replaced_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['planting_date']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.tree_id} ({self.species})"

    def save(self, *args, **kwargs):
        # Ensure tree_id
        if not self.tree_id:
            # simple unique id
            import uuid
            self.tree_id = f"TAWI-{uuid.uuid4().hex[:10].upper()}"

        super().save(*args, **kwargs)

        # generate QR if missing
        if not self.qr_image:
            try:
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                base = getattr(settings, 'SITE_BASE_URL', '')
                target = (base.rstrip('/') if base else '') + f"/trees/{self.pk}/"
                qr.add_data(target)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')
                buf = BytesIO()
                img.save(buf, format='PNG')
                fname = f"{self.tree_id}.png"
                self.qr_image.save(fname, ContentFile(buf.getvalue()), save=False)
                buf.close()
                super().save(update_fields=['qr_image'])
            except Exception:
                # fail silently in save to avoid blocking
                pass

class TreeUpdate(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='updates')
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=Tree.STATUS_CHOICES)
    height_cm = models.FloatField(null=True, blank=True)
    canopy_cm = models.FloatField(null=True, blank=True)
    diameter_cm = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    # link to media records
    media = models.ManyToManyField('media_app.Media', blank=True)

    class Meta:
        ordering = ['-date', '-id']

    @property
    def growth_rate_per_day(self):
        # compute growth rate based on previous update height
        try:
            # prefer previous update with date <= this date
            prev = None
            qs = TreeUpdate.objects.filter(tree=self.tree).exclude(pk=self.pk).order_by('-date', '-id')
            for candidate in qs:
                if candidate.date <= self.date:
                    prev = candidate
                    break
            if not prev:
                # fallback to nearest by date (first/last)
                prev = TreeUpdate.objects.filter(tree=self.tree).exclude(pk=self.pk).order_by('date', 'id').last()
            if not prev or not self.height_cm or not prev.height_cm:
                return None
            days = (self.date - prev.date).days
            if days <= 0:
                days = 1
            return round((self.height_cm - prev.height_cm) / days, 4)
        except Exception:
            return None

    def __str__(self):
        return f"Update {self.id} for {self.tree.tree_id}"
