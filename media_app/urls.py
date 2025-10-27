from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MediaViewSet,
    media_list_view,
    media_upload_view,
    media_map_view,
    media_detail_view,
    media_edit_view,
    media_delete_view,
)

router = DefaultRouter()
router.register(r'media', MediaViewSet, basename='media')

urlpatterns = [
    path('', media_list_view, name='media_list'),
    path('media/gallery/', media_list_view, name='media-gallery'),
    path('media/upload/', media_upload_view, name='media-upload'),
    # alias with underscore used in some templates/tests
    path('media/upload/', media_upload_view, name='media_upload'),
    # underscored and alternate aliases for templates
    path('media/gallery/', media_list_view, name='media_gallery'),
    path('media/map/', media_map_view, name='media_map'),
    path('media/map/', media_map_view, name='media-map'),
    path('media/<int:pk>/', media_detail_view, name='media_detail'),
    path('media/<int:pk>/edit/', media_edit_view, name='media_edit'),
    path('media/<int:pk>/delete/', media_delete_view, name='media_delete'),
    path('', include(router.urls)),
]

# Application namespace used by templates that reverse names like
# {% url 'media_app:media_list' %}
app_name = 'media_app'
