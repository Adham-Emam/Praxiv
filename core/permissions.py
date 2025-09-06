from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow league owners to edit/delete.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
