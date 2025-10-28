from django.shortcuts import render, redirect, get_object_or_404
from .models import GeneratedReport
from .forms import CreateReportForm


def reports_dashboard(request):
    return render(request, 'reports/reports_dashboard.html')


def report_list_view(request):
    reports = GeneratedReport.objects.all()
    return render(request, 'reports/report_downloads.html', {'reports': reports})


def report_create_view(request):
    if request.method == 'POST':
        form = CreateReportForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            rpt = GeneratedReport.objects.create(name=data['name'], report_type=data['report_type'], filters={})
            # Use the namespaced URL so reversing works whether the app is included
            # with a namespace (recommended) or via top-level aliases.
            return redirect('reports:report_detail', pk=rpt.pk)
    else:
        form = CreateReportForm()
    return render(request, 'reports/report_create.html', {'form': form})


def report_detail_view(request, pk):
    rpt = get_object_or_404(GeneratedReport, pk=pk)
    return render(request, 'reports/report_detail.html', {'report': rpt})
 

def report_overview(request):
    """Render the report overview dashboard using minimal context."""
    # Provide simple stats using GeneratedReport model
    total_reports = GeneratedReport.objects.count()
    completed_reports = GeneratedReport.objects.filter(status='Completed').count()
    pending_reports = GeneratedReport.objects.filter(status='Pending').count()
    cancelled_reports = GeneratedReport.objects.filter(status='Cancelled').count()
    recent_reports = GeneratedReport.objects.order_by('-created_at')[:10]
    context = {
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'cancelled_reports': cancelled_reports,
        'recent_reports': recent_reports,
    }
    return render(request, 'reports/report_overview.html', context)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from trees.models import Tree

@api_view(['GET'])
def summary_stats(request):
    total = Tree.objects.count()
    alive = Tree.objects.filter(status='alive').count()
    dead = Tree.objects.filter(status='dead').count()
    survival_rate = (alive / total * 100) if total else 0
    return Response({
        'total_trees': total,
        'alive': alive,
        'dead': dead,
        'survival_rate_percent': round(survival_rate, 2),
    })
