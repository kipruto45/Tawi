from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import GeneratedReportViewSet
from . import views

router = DefaultRouter()
router.register(r'generated', GeneratedReportViewSet, basename='generatedreports')

urlpatterns = [
    path('web/dashboard/', views.reports_dashboard, name='reports-dashboard'),
    path('web/list/', views.report_list_view, name='reports-list'),
    path('web/create/', views.report_create_view, name='reports-create'),
    path('web/detail/<uuid:pk>/', views.report_detail_view, name='report-detail'),
    # Backwards-compatible alias names used by templates (underscore vs hyphen)
    path('web/detail/<uuid:pk>/', views.report_detail_view, name='report_detail'),
    path('web/download/<uuid:pk>/', views.report_detail_view, name='report_download'),
    path('web/list/', views.report_list_view, name='report_list'),
    path('web/create/', views.report_create_view, name='report_create'),
    path('web/detail/<uuid:pk>/', views.report_detail_view, name='report_edit'),
    path('', include(router.urls)),
]

# Namespace used by templates that call names like {% url 'reports:reports-list' %}
app_name = 'reports'
