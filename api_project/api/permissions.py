from rest_framework import permissions

"""
Custom Permission Classes for API

These permission classes provide granular access control for API endpoints,
extending DRF's built-in permissions with role-based and object-level access.
"""


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows:
    - Admin/staff users: Full access (GET, POST, PUT, DELETE)
    - Regular authenticated users: Read-only access (GET)
    - Unauthenticated users: No access
    
    Usage: permission_classes = [IsAdminOrReadOnly]
    """
    def has_permission(self, request, view):
        # Allow GET requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Only admin/staff can modify
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that allows:
    - Object owner: Full access (GET, POST, PUT, DELETE)
    - Other authenticated users: Read-only access (GET)
    - Unauthenticated users: No access
    
    Assumes the model has an 'owner' field.
    Usage: permission_classes = [IsOwnerOrReadOnly]
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Only owner can modify
        return obj.owner == request.user if hasattr(obj, 'owner') else False


class IsStaffUser(permissions.BasePermission):
    """
    Permission that allows only staff/admin users to access.
    
    Usage: permission_classes = [IsStaffUser]
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CanViewBook(permissions.BasePermission):
    """
    Permission based on model permissions.
    Allows users with 'can_view_book' permission.
    
    Usage: permission_classes = [CanViewBook]
    """
    def has_permission(self, request, view):
        return request.user and request.user.has_perm('api.view_book')
