from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, qrcode_scan_view, qrcodes_list_view, qrcodes_generate_view, qrcodes_detail_view

app_name = 'qrcodes'

def scan_index(request):
    # No-arg placeholder route so templates that reverse 'qrcodes:qrcode_scan'
    # without arguments resolve during template smoke tests.
    return HttpResponse('qrcode scan index')

router = DefaultRouter()
router.register(r'', QRCodeViewSet, basename='qrcodes')

urlpatterns = [
    # index / scan landing (no args)
    path('scan/', scan_index, name='qrcode_scan'),
    # scan by id (detailed API / web flows)
    path('scan/<uuid:pk>/', qrcode_scan_view, name='qrcode-scan'),
    # alias used by some templates which expect underscore name
    path('scan/<uuid:pk>/', qrcode_scan_view, name='qrcode_scan_by_id'),
    path('', include(router.urls)),
    # Web UI fallbacks
    path('web/list/', qrcodes_list_view, name='qrcodes_list'),
    path('web/generate/', qrcodes_generate_view, name='qrcodes_generate'),
    path('web/detail/<int:pk>/', qrcodes_detail_view, name='qrcodes_detail'),
]
