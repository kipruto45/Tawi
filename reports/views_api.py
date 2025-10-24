from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import GeneratedReport
from .serializers import GeneratedReportSerializer, CreateReportSerializer
from django.utils import timezone
import json
import io
try:
    # reportlab is optional for PDF generation; import lazily below.
    # Keep a sentinel here in case environments have reportlab installed.
    from reportlab.lib.utils import ImageReader  # type: ignore
except Exception:
    ImageReader = None  # noqa: F821
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None
import tempfile
from django.db import models
from django.core.files.base import ContentFile
from django.conf import settings
from .permissions import IsReportOwnerOrAdmin
import base64


class GeneratedReportViewSet(viewsets.ModelViewSet):
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsReportOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        ser = CreateReportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        # create record
        rpt = GeneratedReport.objects.create(name=data['name'], report_type=data.get('report_type','summary'),
                                             period_start=data.get('period_start'), period_end=data.get('period_end'),
                                             filters=data.get('filters',{}), created_by=request.user)
        # placeholder: use summary_stats for content and save as text file
        from reports.views import summary_stats
        # call summary stats view directly (returns DRF Response)
        resp = summary_stats(request._request)
        content = json.dumps(resp.data, default=str, indent=2).encode('utf-8')
        filename = f'{rpt.id}.json'
        rpt.set_file(filename, content)
        rpt.summary_text = f"Generated at {timezone.now().isoformat()}"
        rpt.save()
        return Response(GeneratedReportSerializer(rpt).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        rpt = self.get_object()
        if not rpt.file:
            return Response({'detail':'file not available'}, status=status.HTTP_404_NOT_FOUND)
        from django.shortcuts import redirect
        return redirect(rpt.file.url)

    @action(detail=True, methods=['post'], url_path='download_pdf')
    def download_pdf(self, request, pk=None):
        rpt = self.get_object()
        # Generate a branded PDF with embedded charts using matplotlib + ReportLab
        # Lazy-import reportlab so the app can start without it installed.
        try:
            from reportlab.lib.pagesizes import A4  # type: ignore
            from reportlab.pdfgen import canvas  # type: ignore
            # ImageReader may have been set at module-import time; prefer the imported one
            if ImageReader is None:
                from reportlab.lib.utils import ImageReader as _ImageReader  # type: ignore
                ImageReaderLocal = _ImageReader
            else:
                ImageReaderLocal = ImageReader
        except Exception:
            return Response({'detail': 'reportlab is not available on server'}, status=status.HTTP_400_BAD_REQUEST)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        # Header / Branding
        p.setFont('Helvetica-Bold', 18)
        p.drawString(40, 820, getattr(settings, 'ORG_NAME', 'Tawi Tree Planting'))
        p.setFont('Helvetica', 12)
        p.drawString(40, 800, f"Report: {rpt.name}")
        p.setFont('Helvetica', 9)
        p.drawString(40, 786, f"Generated: {timezone.localtime(rpt.created_at).strftime('%Y-%m-%d %H:%M')}")

        # Build simple chart data from associated metadata or cached summary
        chart_data = None
        try:
            if rpt.metadata and isinstance(rpt.metadata, dict) and rpt.metadata.get('chart'):  # allow precomputed
                chart_data = rpt.metadata.get('chart')
            else:
                # fallback: sample simple data from summary_text if JSON
                if rpt.file and rpt.file.name.endswith('.json'):
                    try:
                        raw = rpt.file.read().decode('utf-8')
                        parsed = json.loads(raw)
                        # assume parsed contains species distribution or counts
                        if isinstance(parsed, dict):
                            chart_data = parsed.get('species_distribution') or parsed
                    except Exception:
                        chart_data = None
        except Exception:
            chart_data = None

        # Create matplotlib figure if we have numeric chart_data
        img_reader = None
        if chart_data and isinstance(chart_data, dict) and plt and ImageReaderLocal:
            labels = list(chart_data.keys())[:6]
            values = [float(chart_data[k]) for k in labels]
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            fig.savefig(tmp.name, bbox_inches='tight', dpi=150)
            plt.close(fig)
            try:
                img_reader = ImageReaderLocal(tmp.name)
            except Exception:
                img_reader = None

        # Place chart on page if present
        y = 740
        if img_reader:
            p.drawImage(img_reader, 40, y-200, width=300, height=180)
            y -= 210

        # Body text (summary)
        p.setFont('Helvetica', 10)
        body_y = y
        if rpt.summary_text:
            for line in rpt.summary_text.splitlines():
                p.drawString(40, body_y, line[:100])
                body_y -= 14
                if body_y < 60:
                    p.showPage()
                    body_y = 800

        # Footer
        p.setFont('Helvetica-Oblique', 8)
        p.drawString(40, 40, getattr(settings, 'ORG_TAGLINE', 'Growing communities, one tree at a time'))

        p.showPage()
        p.save()
        buffer.seek(0)
        filename = f'{rpt.id}.pdf'
        rpt.set_file(filename, buffer.read())
        return Response({'detail': 'pdf generated', 'url': rpt.file.url})

    @action(detail=True, methods=['post'], url_path='download_xlsx')
    def download_xlsx(self, request, pk=None):
        rpt = self.get_object()
        # openpyxl is optional; import lazily so app can start without it
        try:
            import openpyxl
        except Exception:
            return Response({'detail': 'openpyxl not available on server'}, status=status.HTTP_400_BAD_REQUEST)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Report'
        ws.append(['Report', rpt.name])
        ws.append(['Created at', rpt.created_at.strftime('%Y-%m-%d %H:%M')])

        # If metadata contains tabular sections, write them to sheets
        if rpt.metadata and isinstance(rpt.metadata, dict):
            # write main metadata
            ws.append([])
            ws.append(['Metadata'])
            for k, v in rpt.metadata.items():
                if k == 'chart':
                    continue
                ws.append([k, json.dumps(v)])

        # If JSON file exists, attempt to flatten simple dict to sheet
        if rpt.file and rpt.file.name.endswith('.json'):
            try:
                import json as _json
                raw = rpt.file.read().decode('utf-8')
                data = _json.loads(raw)
                if isinstance(data, dict):
                    sheet = wb.create_sheet('Snapshot')
                    sheet.append(['Key', 'Value'])
                    for k, v in data.items():
                        sheet.append([k, str(v)])
            except Exception:
                pass

        # Attempt to insert chart image as a sheet image (xlsx supports images)
        chart_file = None
        if rpt.metadata and isinstance(rpt.metadata, dict) and rpt.metadata.get('chart') and plt:
            try:
                chart = rpt.metadata.get('chart')
                labels = list(chart.keys())[:6]
                values = [float(chart[k]) for k in labels]
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(labels, values)
                tmp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                fig.savefig(tmp.name, bbox_inches='tight', dpi=150)
                plt.close(fig)
                from openpyxl.drawing.image import Image as XLImage
                img = XLImage(tmp.name)
                img.anchor = 'A1'
                ws.add_image(img)
            except Exception:
                pass

        bio = io.BytesIO()
        wb.save(bio)
        bio.seek(0)
        filename = f'{rpt.id}.xlsx'
        rpt.set_file(filename, bio.read())
        return Response({'detail': 'xlsx generated', 'url': rpt.file.url})

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        # simple stats: counts by type
        qs = self.get_queryset()
        data = qs.values('report_type').annotate(count=models.Count('id'))
        return Response({'counts': list(data)})
