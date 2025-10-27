from django.urls import path
from . import views

# Application namespace used by templates and `include(..., namespace=...)`
app_name = 'dashboard'
from .api_views import (
    DashboardSummaryAPIView,
    DashboardTrendsAPIView,
    DashboardSpeciesAPIView,
    DashboardRegionsAPIView,
)

urlpatterns = [
    # web route
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.dashboard_admin, name='admin_dashboard'),
    # backward compatible alias used in some templates/tests
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    # field officer dashboard
    path('field/', views.dashboard_field, name='dashboard_field'),
    # alias used in some templates
    path('field/officer/', views.dashboard_field, name='dashboard_field_officer'),
    path('field/tasks/', views.assigned_tasks, name='assigned_tasks'),
    path('volunteers/', views.volunteers_list, name='volunteers_list'),
    path('volunteer/', views.dashboard_volunteer, name='dashboard_volunteer'),
    path('partner/contributions/', views.my_contributions, name='my_contributions'),
    path('partner/', views.dashboard_partner, name='dashboard_partner'),
    path('community/', views.dashboard_community, name='dashboard_community'),
    # Guest-specific dashboard should render the guest template
    path('guest/', views.dashboard_guest, name='dashboard_guest'),
    path('project/', views.dashboard_project, name='dashboard_project'),
    path('insights/', views.insights_dashboard, name='insights_dashboard'),
    # api
    path('api/summary/', DashboardSummaryAPIView.as_view(), name='dashboard_summary_api'),
    path('api/trends/', DashboardTrendsAPIView.as_view(), name='dashboard_trends_api'),
    path('api/species/', DashboardSpeciesAPIView.as_view(), name='dashboard_species_api'),
    path('api/regions/', DashboardRegionsAPIView.as_view(), name='dashboard_regions_api'),
]
