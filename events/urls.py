from django.urls import path
from . import views

urlpatterns = [
    path('upcoming/', views.upcoming_events, name='upcoming_events'),
    path('upcoming/<int:pk>/', views.event_detail, name='upcoming_event_detail'),
    path('upcoming/<int:pk>/participate/', views.participate, name='upcoming_event_participate'),
]
