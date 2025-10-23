from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import QRCode
from .serializers import QRCodeSerializer, GenerateQRCodeSerializer
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


class QRCodeViewSet(viewsets.ModelViewSet):
    queryset = QRCode.objects.select_related('tree','site').all()
    serializer_class = QRCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        serializer = GenerateQRCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        tree = None
        site = None
        if data.get('tree_id'):
            from trees.models import Tree
            try:
                tree = Tree.objects.get(tree_id=data['tree_id'])
            except Tree.DoesNotExist:
                tree = None
        if data.get('site_id'):
            from beneficiaries.models import PlantingSite
            try:
                site = PlantingSite.objects.get(pk=data['site_id'])
            except PlantingSite.DoesNotExist:
                site = None
        qr = QRCode.objects.create(tree=tree, site=site, label=data.get('label',''))
        qr.generate_image(request.build_absolute_uri('/'))
        qr.save()
        return Response(QRCodeSerializer(qr).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        qr = self.get_object()
        if not qr.image:
            qr.generate_image(request.build_absolute_uri('/'))
            qr.save()
        return redirect(qr.image.url)


@api_view(['GET'])
def qrcode_scan_view(request, pk):
    # public endpoint — log scan and redirect to a friendly view
    qr = get_object_or_404(QRCode, pk=pk)
    now = timezone.now()
    try:
        qr.increment_scan(now)
    except Exception:
        # fallback: increment in-memory
        qr.scan_count = (qr.scan_count or 0) + 1
        qr.last_scanned = now
        qr.save()
    # redirect to a public info page (could be same app)
    if qr.tree:
        return redirect(qr.tree.get_absolute_url())
    if qr.site:
        return redirect('/planting-site/%s/' % qr.site.pk)
    # otherwise show a simple scan result
    return render(request, 'qrcodes/qrcode_scan_result.html', {'qr': qr})


@login_required
def qrcodes_list_view(request):
    # simple paginated list for web UI
    qrcodes = QRCode.objects.all().order_by('-created_at')
    paginator = Paginator(qrcodes, 20)
    page = request.GET.get('page')
    qrcodes_page = paginator.get_page(page)
    return render(request, 'qrcodes/qrcodes_list.html', {'qrcodes': qrcodes_page})


@login_required
def qrcodes_generate_view(request):
    # Render the generator form and on POST create a QRCode via existing API logic
    generated_qrcode = None
    if request.method == 'POST':
        tree_id = request.POST.get('tree_id')
        site_id = request.POST.get('site_id')
        label = request.POST.get('label')
        qr = QRCode.objects.create(label=label)
        try:
            qr.generate_image(request.build_absolute_uri('/'))
            qr.save()
            generated_qrcode = qr
        except Exception:
            generated_qrcode = qr
    return render(request, 'qrcodes/qrcodes_generate.html', {'generated_qrcode': generated_qrcode})


@login_required
def qrcodes_detail_view(request, pk):
    qr = get_object_or_404(QRCode, pk=pk)
    return render(request, 'qrcodes/qrcodes_detail.html', {'qrcode': qr})
