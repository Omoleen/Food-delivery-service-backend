from rest_framework.permissions import IsAuthenticated, BasePermission
from users.models import User


class IsVendorOrVendorEmployeeOrRider(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR or request.user.role == User.Role.VENDOR_EMPLOYEE or request.user.role == User.Role.RIDER:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor == request.user or obj.vendor.employee.filter(employee=request.user).exists() or obj.rider == request.user:
                return True
        return False


class IsVendorOrRider(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR or request.user.role == User.Role.RIDER:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor == request.user or obj.rider == request.user:
                return True
        return False

