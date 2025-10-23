from django.core.cache import cache
from django.db.models import Avg, Count
from monitoring.models import MonitoringReport


def get_report_summary_cached(key='reports:summary', ttl=300):
    data = cache.get(key)
    if data:
        return data
    # example aggregation
    qs = MonitoringReport.objects.all()
    total_reports = qs.count()
    avg_surv = qs.exclude(total_planted=0).aggregate(avg=Avg((__import__('django').db.models.F('surviving')*1.0)/__import__('django').db.models.F('total_planted')*100))['avg']
    data = {'total_reports': total_reports, 'avg_survival': round(avg_surv or 0,2)}
    cache.set(key, data, ttl)
    return data
