from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_to', 'status', 'deadline')
    list_filter = ('status',)
    search_fields = ('name', 'location', 'assigned_to__username')
