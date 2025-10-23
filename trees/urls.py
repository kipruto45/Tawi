from django.urls import path
from . import web_views, web_public_views

app_name = 'trees'

urlpatterns = [
    path('public/', web_views.tree_list, name='tree_list_public_fallback'),
    path('public/list/', web_views.tree_list, name='tree_list_public_fallback2'),
    # Public listing for guests (non-destructive)
    path('public/planted/', web_public_views.trees_planted_public, name='trees_planted_public'),
    path('', web_views.tree_list, name='tree_list'),
    path('add/', web_views.tree_add, name='tree_add'),
    path('web/add/', web_views.tree_add_view, name='tree_add_web'),
    path('web/dashboard/', web_views.trees_dashboard_view, name='trees_dashboard'),
    path('web/growth/add/', web_views.growth_record_add_view, name='growth_record_add'),
    path('<int:pk>/', web_views.tree_detail, name='tree_detail'),
    path('<int:pk>/edit/', web_views.tree_edit, name='tree_edit'),
    path('<int:pk>/delete/', web_views.tree_delete, name='tree_delete'),
]
