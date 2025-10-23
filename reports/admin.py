from django.contrib import admin
from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('name','report_type','created_by','created_at')
    search_fields = ('name','report_type')
    readonly_fields = ('file',)
