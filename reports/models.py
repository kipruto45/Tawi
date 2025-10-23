import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


def reports_upload_to(instance, filename):
    return f'reports/{instance.pk or "new"}/{filename}'


class GeneratedReport(models.Model):
    REPORT_TYPES = (('summary', 'Summary'), ('partner', 'Partner'), ('public', 'Public'))
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=32, choices=REPORT_TYPES, default='summary')
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    filters = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to=reports_upload_to, null=True, blank=True)
    file_type = models.CharField(max_length=16, blank=True)
    summary_text = models.TextField(blank=True)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.name} ({self.created_at.date()})"

    def set_file(self, filename, content):
        from django.core.files.base import ContentFile
        self.file.save(filename, ContentFile(content), save=False)
        self.file_type = filename.split('.')[-1]
        self.save()
