from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, F
from django.shortcuts import render, get_object_or_404, redirect
from .models import FollowUp, MonitoringReport
from .serializers import FollowUpSerializer, MonitoringReportSerializer, MonitoringStatsSerializer


class FollowUpViewSet(viewsets.ModelViewSet):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MonitoringReportViewSet(viewsets.ModelViewSet):
    queryset = MonitoringReport.objects.select_related('site', 'tree', 'reporter').prefetch_related('media').all()
    serializer_class = MonitoringReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-site/(?P<site_id>[^/.]+)')
    def by_site(self, request, site_id=None):
        qs = self.get_queryset().filter(site__id=site_id)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        qs = self.get_queryset()
        total_reports = qs.count()
        total_sites = qs.values('site').distinct().count()
        # average survival across reports where defined
        surv_qs = qs.exclude(total_planted=0)
        avg_survival = None
        if surv_qs.exists():
            avg_survival = surv_qs.aggregate(avg=Avg((F('surviving')*1.0)/F('total_planted')*100))['avg']
        # monthly trends (simple count & avg survival per month)
        from django.db.models.functions import TruncMonth
        monthly = qs.annotate(month=TruncMonth('date')).values('month').annotate(count=Count('id'), avg_surv=Avg((F('surviving')*1.0)/F('total_planted')*100)).order_by('month')[:24]
        monthly_trends = [{'month': m['month'].strftime('%Y-%m') if m['month'] else None, 'count': m['count'], 'avg_survival': round(m['avg_surv'] or 0,2)} for m in monthly]
        # top sites by avg survival
        top = qs.values('site__id', 'site__name').annotate(avg_surv=Avg((F('surviving')*1.0)/F('total_planted')*100)).order_by('-avg_surv')[:10]
        top_sites = [{'site_id': t['site__id'], 'site_name': t['site__name'], 'avg_survival': round(t['avg_surv'] or 0,2)} for t in top]
        payload = {
            'total_reports': total_reports,
            'total_monitored_sites': total_sites,
            'avg_survival_rate': round(avg_survival or 0,2) if avg_survival is not None else None,
            'monthly_trends': monthly_trends,
            'top_sites': top_sites,
        }
        serializer = MonitoringStatsSerializer(payload)
        return Response(serializer.data)


# --- template-based views ---
def monitoring_list_view(request):
    reports = MonitoringReport.objects.select_related('site', 'tree', 'reporter').all()[:500]
    return render(request, 'monitoring/monitoring_list.html', {'reports': reports})


def monitoring_detail_view(request, pk):
    report = get_object_or_404(MonitoringReport, pk=pk)
    return render(request, 'monitoring/monitoring_detail.html', {'report': report})


def monitoring_add_view(request):
    if request.method == 'POST':
        site_id = request.POST.get('site')
        tree_id = request.POST.get('tree')
        total_planted = int(request.POST.get('total_planted') or 0)
        surviving = int(request.POST.get('surviving') or 0)
        health_status = request.POST.get('health_status')
        notes = request.POST.get('growth_notes')
        site = None
        tree = None
        from beneficiaries.models import PlantingSite
        from trees.models import Tree
        if site_id:
            try:
                site = PlantingSite.objects.get(id=site_id)
            except PlantingSite.DoesNotExist:
                site = None
        if tree_id:
            try:
                tree = Tree.objects.get(tree_id=tree_id)
            except Tree.DoesNotExist:
                tree = None
        report = MonitoringReport.objects.create(site=site, tree=tree, reporter=request.user if request.user.is_authenticated else None,
                                                 total_planted=total_planted, surviving=surviving, health_status=health_status or 'healthy',
                                                 growth_notes=notes or '')
        return redirect('monitoring-web-detail', pk=report.pk)
    return render(request, 'monitoring/monitoring_add.html')


def monitoring_map_view(request):
    return render(request, 'monitoring/monitoring_map.html')


def monitoring_dashboard_view(request):
    return render(request, 'monitoring/monitoring_dashboard.html')
