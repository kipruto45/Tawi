from rest_framework import permissions


class IsReportOwnerOrAdmin(permissions.BasePermission):
    """Allow access if user is staff or the creator of the report."""

    def has_permission(self, request, view):
        # list/create allowed for authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # Allow access to system-generated reports (no creator) and public reports
        if getattr(obj, 'created_by', None) is None:
            return True
        if getattr(obj, 'report_type', None) == 'public':
            return True
        return getattr(obj, 'created_by', None) == request.user
from rest_framework import permissions


class IsReportAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or getattr(request.user, 'role', '') == 'admin'))

