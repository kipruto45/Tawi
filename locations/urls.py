from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.location_map, name='location_map'),
]
