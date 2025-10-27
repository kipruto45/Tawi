from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.submit_feedback, name='feedback'),
    path('submit/', views.submit_feedback, name='submit'),
]
