from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, qrcode_scan_view, qrcodes_list_view, qrcodes_generate_view, qrcodes_detail_view

router = DefaultRouter()
router.register(r'', QRCodeViewSet, basename='qrcodes')

urlpatterns = [
    path('scan/<uuid:pk>/', qrcode_scan_view, name='qrcode-scan'),
    # alias used by templates (underscore vs hyphen)
    path('scan/<uuid:pk>/', qrcode_scan_view, name='qrcode_scan'),
    path('', include(router.urls)),
    # Web UI fallbacks
    path('web/list/', qrcodes_list_view, name='qrcodes_list'),
    path('web/generate/', qrcodes_generate_view, name='qrcodes_generate'),
    path('web/detail/<int:pk>/', qrcodes_detail_view, name='qrcodes_detail'),
]
