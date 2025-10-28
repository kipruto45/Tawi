from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FollowUpViewSet, MonitoringReportViewSet
from . import views

router = DefaultRouter()
router.register(r'followups', FollowUpViewSet)
router.register(r'reports', MonitoringReportViewSet, basename='monitoring')

urlpatterns = [
    path('web/list/', views.monitoring_list_view, name='monitoring-web-list'),
    path('web/add/', views.monitoring_add_view, name='monitoring-add'),
    path('web/detail/<int:pk>/', views.monitoring_detail_view, name='monitoring-web-detail'),
    path('web/map/', views.monitoring_map_view, name='monitoring-web-map'),
    path('web/dashboard/', views.monitoring_dashboard_view, name='monitoring-web-dashboard'),
    # Backwards-compatible aliases for templates that expect underscored names
    path('web/list/', views.monitoring_list_view, name='monitoring_list'),
    path('web/add/', views.monitoring_add_view, name='add_monitoring'),
    path('web/add/', views.monitoring_add_view, name='add_followup'),
    path('web/detail/<int:pk>/', views.monitoring_detail_view, name='monitoring_detail'),
    path('web/detail/<int:pk>/', views.monitoring_detail_view, name='monitoring_edit'),
    path('web/detail/<int:pk>/', views.monitoring_detail_view, name='monitoring_delete'),
    path('', include(router.urls)),
]

# Define namespace so templates can reverse 'monitoring:...'
app_name = 'monitoring'
