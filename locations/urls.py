from django.urls import path
from . import views

urlpatterns = [
    path('', views.location_map, name='locations'),
    path('map/', views.location_map, name='location_map'),
]
