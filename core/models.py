from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp}: {self.action} by {self.user}"

class Notification(models.Model):
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient}: {self.subject}"


class Post(models.Model):
    """Announcements / blog posts"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    author = models.CharField(max_length=255, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class SiteConfiguration(models.Model):
    """Simple key configuration for site-wide settings"""
    site_name = models.CharField(max_length=255, default='Tawi Tree Planting')
    contact_email = models.EmailField(blank=True)
    google_maps_api_key = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.site_name


class Partner(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MessageSent(models.Model):
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)
    sender = models.CharField(max_length=255, blank=True)
    recipients_count = models.PositiveIntegerField(default=0)
    recipients_preview = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"MessageSent {self.id} by {self.sender}"


class MessageRecipient(models.Model):
    message = models.ForeignKey(MessageSent, on_delete=models.CASCADE, related_name='recipients')
    email = models.EmailField()
    status = models.CharField(max_length=50, default='pending')
    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recipient {self.email} for message {self.message_id}"
