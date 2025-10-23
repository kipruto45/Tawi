from django.contrib import admin
from .models import QRCode


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'tree', 'site', 'scan_count', 'last_scanned', 'created_at')
    search_fields = ('label','tree__tree_id','site__name')
    readonly_fields = ('image', 'scan_count', 'last_scanned', 'created_at')
