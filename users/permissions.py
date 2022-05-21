from rest_framework import permissions


class UserPermissions(permissions.BasePermission):
    """User permissions"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # allow logged user to edit own details
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj == request.user or request.user.is_superuser
        # allow superusers to edit details
        return True
