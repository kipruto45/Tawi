from django.contrib import admin
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('id', 'donor', 'amount', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('donor__username', 'donor__email')
    ordering = ('-date',)
    date_hierarchy = 'date'
    list_per_page = 50
    readonly_fields = ('id',)
    actions = ['mark_completed', 'mark_pending', 'export_as_csv']

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='Completed')
        self.message_user(request, f"{updated} donation(s) marked as Completed.")
    mark_completed.short_description = 'Mark selected donations as Completed'

    def mark_pending(self, request, queryset):
        updated = queryset.update(status='Pending')
        self.message_user(request, f"{updated} donation(s) marked as Pending.")
    mark_pending.short_description = 'Mark selected donations as Pending'

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        meta = self.model._meta
        field_names = ['id', 'donor', 'amount', 'status', 'date']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=donations.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, f) if f != 'donor' else (obj.donor.username if obj.donor else '') for f in field_names])
        return response
    export_as_csv.short_description = 'Export selected donations as CSV'
