from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .models import Media
from .serializers import MediaSerializer
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


class IsUploaderOrAdmin:
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and getattr(request.user, 'role', '') == 'admin':
            return True
        return obj.uploader == request.user


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.select_related('uploader').all().order_by('-uploaded_at')
    serializer_class = MediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ['uploader__id', 'tree__tree_id', 'site__id']

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.uploader != request.user and not request.user.is_staff:
            return Response({'detail':'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_location(self, request, lat=None, lon=None):
        qs = self.get_queryset().filter(latitude__isnull=False, longitude__isnull=False)
        # simple proximity filter: within ~0.01 degrees
        try:
            latf = float(lat); lonf = float(lon)
            qs = qs.filter(latitude__gte=latf-0.01, latitude__lte=latf+0.01, longitude__gte=lonf-0.01, longitude__lte=lonf+0.01)
        except Exception:
            qs = qs.none()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response({'status':'success','data':serializer.data})

    
# Template-based views for the media app
def media_list_view(request):
    qs = Media.objects.all().order_by('-uploaded_at')[:200]
    # Build a display list: images first, then non-image media (videos/docs) up to `target`
    image_items = [m for m in qs if m.file_type == 'image' and getattr(m.file, 'url', None)]
    non_image_items = [m for m in qs if m.file_type != 'image']
    target = 10
    display_items = []
    # take images first
    for m in image_items:
        if len(display_items) >= target:
            break
        display_items.append(m)
    # fill with non-image items
    if len(display_items) < target:
        for m in non_image_items:
            if len(display_items) >= target:
                break
            display_items.append(m)

    placeholders = []
    if len(display_items) < target:
        placeholders = list(range(target - len(display_items)))

    # If the visitor is anonymous, show the guest-oriented gallery template
    if not request.user.is_authenticated:
        # The guest template is a more visual, read-only gallery
        return render(request, 'media_app/media_guests_list.html', {
            'media_list': qs,
            'display_items': display_items,
            'placeholders': placeholders,
        })
    return render(request, 'media_app/media_list.html', {'media_list': qs})

@login_required
def media_upload_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        f = request.FILES.get('file')
        tree_id = request.POST.get('tree')
        if f:
            m = Media.objects.create(title=title or '', file=f, uploader=request.user)
            return render(request, 'media_app/media_detail.html', {'media': m})
    return render(request, 'media_app/media_upload.html')

def media_map_view(request):
    return render(request, 'media_app/media_map.html')


def media_detail_view(request, pk):
    """Render a simple media detail page used by the admin/media templates.

    This is intentionally lightweight: if the template exists it will be used,
    otherwise a minimal HTTP 200 response with the media title is returned.
    """
    try:
        m = Media.objects.get(pk=pk)
    except Media.DoesNotExist:
        from django.http import Http404

        raise Http404("Media not found")
    template_name = 'media_app/media_detail.html'
    return render(request, template_name, {'media': m})


def media_edit_view(request, pk):
    try:
        m = Media.objects.get(pk=pk)
    except Media.DoesNotExist:
        from django.http import Http404

        raise Http404("Media not found")

    # only uploader or staff can edit
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if m.uploader != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        title = request.POST.get('title')
        if title is not None:
            m.title = title
            m.save()
            return render(request, 'media_app/media_detail.html', {'media': m})
    return render(request, 'media_app/media_edit.html', {'media': m})


def media_delete_view(request, pk):
    try:
        m = Media.objects.get(pk=pk)
    except Media.DoesNotExist:
        from django.http import Http404

        raise Http404("Media not found")

    # only uploader or staff can delete
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if m.uploader != request.user and not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        m.delete()
        return redirect('media_list')
    return render(request, 'media_app/media_confirm_delete.html', {'media': m})
