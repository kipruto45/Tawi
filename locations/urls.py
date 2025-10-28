from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_map, name='locations'),
    path('map/', views.location_map, name='location_map'),
    path('add/', views.add_site, name='add_site'),
    path('<int:pk>/', views.view_site, name='view_site'),
    path('<int:pk>/edit/', views.edit_site, name='edit_site'),
    path('<int:pk>/delete/', views.delete_site, name='delete_site'),
]
