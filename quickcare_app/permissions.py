from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsDoctorOrStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
                hasattr(request.user, 'doctor') or
                request.user.is_staff
        )


# Add the original permission classes
class IsDoctor(BasePermission):
    """
    Permission to only allow doctors to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'doctor')


class IsPatient(BasePermission):
    """
    Permission to only allow patients to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'patient')


class IsOwnerOrDoctor(BasePermission):
    """
    Permission to only allow owners of an object or the assigned doctor to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is the patient who owns this queue
        if hasattr(request.user, 'patient') and obj.patient.user == request.user:
            return True

        # Check if user is the doctor assigned to this queue
        if hasattr(request.user, 'doctor') and obj.doctor.user == request.user:
            return True

        # Admin can access all
        return request.user.is_staff

