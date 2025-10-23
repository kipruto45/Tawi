from django.db import models
from django.conf import settings
from django.utils import timezone
from beneficiaries.models import PlantingSite
from trees.models import Tree
from io import BytesIO
from PIL import Image, ExifTags
from django.core.files.base import ContentFile
import os


def media_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    return f"media/{instance.uploader_id}/{ts}_{base}{ext}"


class Media(models.Model):
    FILE_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]

    file = models.FileField(upload_to=media_upload_to)
    file_type = models.CharField(max_length=16, choices=FILE_TYPES, default='image')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # generated thumbnail for faster guest gallery rendering
    thumbnail = models.ImageField(upload_to=media_upload_to, null=True, blank=True)

    # links
    tree = models.ForeignKey(Tree, null=True, blank=True, on_delete=models.SET_NULL, related_name='media')
    site = models.ForeignKey(PlantingSite, null=True, blank=True, on_delete=models.SET_NULL, related_name='media')

    # extracted metadata
    latitude = models.FloatField(null=True, blank=True, db_index=True)
    longitude = models.FloatField(null=True, blank=True, db_index=True)
    taken_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Media {self.id} - {self.title or os.path.basename(self.file.name)}"

    def save(self, *args, **kwargs):
        # detect file type
        name = self.file.name.lower()
        if any(name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            self.file_type = 'image'
        elif any(name.endswith(ext) for ext in ['.mp4', '.mov', '.avi']):
            self.file_type = 'video'
        else:
            self.file_type = 'document'

        super().save(*args, **kwargs)

        # if image, try compress and extract exif
        if self.file_type == 'image':
            try:
                self._process_image()
            except Exception:
                pass

    def _process_image(self):
        # open image and reduce size if large
        self.file.open()
        img = Image.open(self.file)
        try:
            exif = {
                ExifTags.TAGS.get(k): v
                for k, v in img._getexif().items()
                if k in ExifTags.TAGS
            }
        except Exception:
            exif = {}

        # extract DateTime and GPS if present
        dt = exif.get('DateTimeOriginal') or exif.get('DateTime')
        if dt and not self.taken_at:
            try:
                self.taken_at = timezone.datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')
            except Exception:
                pass

        gps = exif.get('GPSInfo')
        if gps:
            try:
                def _deg(v):
                    d, m, s = v
                    return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600

                lat = _deg(gps[2]) * (-1 if gps[1] == 'S' else 1)
                lon = _deg(gps[4]) * (-1 if gps[3] == 'W' else 1)
                self.latitude = lat
                self.longitude = lon
            except Exception:
                pass

        # compress if larger than threshold
        buf = BytesIO()
        max_size = 1600
        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / float(max(w, h))
            img = img.resize((int(w*ratio), int(h*ratio)), Image.LANCZOS)

        img.save(buf, format='JPEG', quality=85)
        fname = os.path.basename(self.file.name)
        # overwrite the main file (compressed)
        self.file.save(fname, ContentFile(buf.getvalue()), save=False)

        # also generate a thumbnail (smaller) for guest gallery
        try:
            thumb_buf = BytesIO()
            thumb_max = 600
            tw, th = img.size
            if max(tw, th) > thumb_max:
                tr = thumb_max / float(max(tw, th))
                thumb = img.resize((int(tw*tr), int(th*tr)), Image.LANCZOS)
            else:
                thumb = img.copy()
            thumb.save(thumb_buf, format='JPEG', quality=75)
            thumb_name = f"thumb_{fname}"
            self.thumbnail.save(thumb_name, ContentFile(thumb_buf.getvalue()), save=False)
            thumb_buf.close()
        except Exception:
            # non-critical: if thumbnail generation fails, continue without it
            pass

        buf.close()
        super().save(update_fields=['file', 'thumbnail', 'latitude', 'longitude', 'taken_at'])
