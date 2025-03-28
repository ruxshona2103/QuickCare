from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAdminUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_admin


class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated