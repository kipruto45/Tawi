from django.contrib import admin

# placeholder admin for notifications
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('recipient', 'verb', 'level', 'unread', 'public', 'created_at')
	list_filter = ('level', 'unread', 'public')
	search_fields = ('recipient__username','verb','description')

# placeholder admin for notifications
