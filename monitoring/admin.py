from django.contrib import admin
from .models import FollowUp

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('tree', 'type', 'scheduled_date', 'completed')


from .models import MonitoringReport


@admin.register(MonitoringReport)
class MonitoringReportAdmin(admin.ModelAdmin):
    list_display = ('site', 'tree', 'reporter', 'date', 'survival_rate', 'health_status')
    list_filter = ('health_status', 'date', 'site')
    search_fields = ('site__name', 'tree__tree_id', 'reporter__username')
    readonly_fields = ('survival_rate',)
    filter_horizontal = ('media',)
