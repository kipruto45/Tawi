from django.db import models
from django.conf import settings


class Task(models.Model):
    """Minimal Task/Assignment model for field officers."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_tasks')
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default='pending')
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-deadline', '-created_at']

    def __str__(self):
        return self.name
