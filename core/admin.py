from django.contrib import admin
from .models import ActivityLog, Notification

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject', 'sent', 'created_at')

from .models import Post, SiteConfiguration

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published', 'created_at')

@admin.register(SiteConfiguration)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email')
