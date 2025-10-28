from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet
from . import views

# Provide an app_name so the app can be included with an explicit namespace
app_name = 'notifications'

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('web/list/', lambda r: __import__('django.shortcuts').shortcuts.render(r, 'notifications/notifications_list.html', {'notifications': r.user.notifications.all() if r.user.is_authenticated else []}), name='notifications-list'),
    # Template-compatible alias names
    path('web/list/', lambda r: __import__('django.shortcuts').shortcuts.render(r, 'notifications/notifications_list.html', {'notifications': r.user.notifications.all() if r.user.is_authenticated else []}), name='notifications_list'),
    path('public/', views.notifications_public, name='notifications_public'),
    path('page/', views.notifications_page, name='notifications_page'),
    path('clear/', views.notifications_clear, name='notifications_clear'),
    path('mark/<int:pk>/', views.notifications_mark, name='notifications_mark'),
    path('mark/<int:pk>/', views.notifications_mark, name='notifications_mark_read'),
    path('unmark/<int:pk>/', views.notifications_unmark, name='notifications_unmark'),
    path('delete/<int:pk>/', views.notifications_unmark, name='notifications_delete'),
    path('', include(router.urls)),
]
