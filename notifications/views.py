from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer, SendNotificationSerializer
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().select_related('recipient','actor')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # users only see their notifications unless they have notification admin perms
        try:
            user = self.request.user
            if user.is_authenticated and (user.has_perm('notifications.manage_notifications') or 'Admins' in set(user.groups.values_list('name', flat=True))):
                return super().get_queryset()
        except Exception:
            pass
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = get_object_or_404(Notification, pk=pk)
        try:
            if notif.recipient != request.user:
                user = request.user
                if not (user.is_authenticated and (user.has_perm('notifications.manage_notifications') or 'Admins' in set(user.groups.values_list('name', flat=True)))):
                    return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response(status=status.HTTP_403_FORBIDDEN)
        notif.mark_read()
        return Response({'status':'ok'})

    @action(detail=False, methods=['post'])
    def send(self, request):
        # admin-only endpoint to create & optionally dispatch a notification
        try:
            if not (request.user.is_authenticated and (request.user.has_perm('notifications.manage_notifications') or 'Admins' in set(request.user.groups.values_list('name', flat=True)))):
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rd = serializer.validated_data
        recipient_id = rd['recipient_id']
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response({'detail':'recipient not found'}, status=status.HTTP_400_BAD_REQUEST)
        notif = Notification.objects.create(recipient=recipient, actor=request.user, verb=rd['verb'], description=rd.get('description',''), url=rd.get('url',''), level=rd.get('level','info'))
        return Response(NotificationSerializer(notif).data, status=status.HTTP_201_CREATED)


@login_required
def notifications_page(request):
    """Render the provided accounts/notifications.html template for the current user."""
    qs = request.user.notifications.all()
    # paginate (20 per page)
    paginator = Paginator(qs, 20)
    page = request.GET.get('page')
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
        'paginator': paginator,
    })


def notifications_public(request):
    # Show notifications explicitly marked public by admin
    qs = Notification.objects.filter(public=True)
    return render(request, 'notifications/public_notifications.html', {'notifications': qs})


@login_required
@login_required
@require_POST
def notifications_clear(request):
    """Mark all notifications for the current user as read and redirect back to the notifications page.

    This endpoint only accepts POST to avoid doing state changes via GET.
    """
    qs = request.user.notifications.filter(unread=True)
    # bulk update for performance
    if qs.exists():
        qs.update(unread=False)
    return redirect('notifications_page')


@login_required
@require_POST
def notifications_mark(request, pk):
    """AJAX-friendly endpoint to mark a single notification as read and return JSON.

    Expects POST and returns {'ok': True} on success or appropriate status code.
    """
    try:
        notif = request.user.notifications.get(pk=pk)
    except Exception:
        return JsonResponse({'detail': 'not found'}, status=404)

    if notif.unread:
        notif.unread = False
        notif.save(update_fields=['unread'])

    return JsonResponse({'ok': True, 'id': pk})


@login_required
@require_POST
def notifications_unmark(request, pk):
    """AJAX-friendly endpoint to mark a single notification as unread (undo) and return JSON."""
    try:
        notif = request.user.notifications.get(pk=pk)
    except Exception:
        return JsonResponse({'detail': 'not found'}, status=404)

    if not notif.unread:
        notif.unread = True
        notif.save(update_fields=['unread'])

    return JsonResponse({'ok': True, 'id': pk})
