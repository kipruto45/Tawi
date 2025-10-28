from django.contrib import admin
from .models import TreeSpecies, Tree, TreeUpdate
from django.utils.safestring import mark_safe
from django.urls import reverse
from qrcodes.models import QRCode

@admin.register(TreeSpecies)
class TreeSpeciesAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ('tree_id', 'species', 'planting_date', 'beneficiary', 'status', 'qrcode_link')
    readonly_fields = ('qrcode_link',)

    def qrcode_link(self, obj):
        try:
            qr = QRCode.objects.filter(tree=obj).first()
            if not qr:
                return ''
            url = reverse('admin:qrcodes_qrcode_change', args=(qr.pk,))
            return mark_safe(f'<a href="{url}">QR {qr.pk}</a>')
        except Exception:
            return ''
    qrcode_link.short_description = 'QRCode'

@admin.register(TreeUpdate)
class TreeUpdateAdmin(admin.ModelAdmin):
    list_display = ('tree', 'date', 'status')
