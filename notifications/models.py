from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    LEVELS = (('info', 'Info'), ('warning', 'Warning'), ('critical', 'Critical'))
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='actor_notifications')
    verb = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    level = models.CharField(max_length=16, choices=LEVELS, default='info')
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(null=True, blank=True)
    # When True this notification is visible to anonymous/public users
    public = models.BooleanField(default=False)
    delivery_status = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def mark_read(self):
        if self.unread:
            self.unread = False
            self.save(update_fields=['unread'])

    def __str__(self):
        return f"Notif to {self.recipient} — {self.verb}"
