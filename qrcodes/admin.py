from django.contrib import admin
from .models import QRCode
from django.utils.safestring import mark_safe
from django.urls import reverse


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'tree_link', 'site', 'scan_count', 'last_scanned', 'created_at')
    search_fields = ('label','tree__tree_id','site__name')
    readonly_fields = ('image', 'scan_count', 'last_scanned', 'created_at')

    def tree_link(self, obj):
        try:
            if not obj.tree:
                return ''
            url = reverse('admin:trees_tree_change', args=(obj.tree.pk,))
            return mark_safe(f'<a href="{url}">{obj.tree.tree_id}</a>')
        except Exception:
            return ''
    tree_link.short_description = 'Tree'
