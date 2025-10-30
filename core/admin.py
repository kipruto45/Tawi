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

from .models import Partner, MessageSent


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'contact_email', 'created_at')


@admin.register(MessageSent)
class MessageSentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'sender', 'recipients_count', 'created_at')
    readonly_fields = ('subject', 'body', 'sender', 'recipients_count', 'recipients_preview', 'created_at')

from .models import MessageRecipient


@admin.register(MessageRecipient)
class MessageRecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'message', 'status', 'created_at')
    readonly_fields = ('email', 'message', 'status', 'error', 'created_at')
