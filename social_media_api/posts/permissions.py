"""Custom permissions: only the owner can edit or delete their posts/comments."""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read (GET, HEAD, OPTIONS) to anyone; allow write (POST, PUT, PATCH, DELETE)
    only to the owner of the object.
    For Post: owner is obj.author; for Comment: owner is obj.user.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, "author"):
            return obj.author == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False
