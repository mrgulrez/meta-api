from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only managers to modify/delete menu items.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name='managers').exists()