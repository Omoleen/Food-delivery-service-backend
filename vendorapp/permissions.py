from rest_framework.permissions import IsAuthenticated, BasePermission
from users.models import User


class IsVendor(IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor == request.user:
                return True
        return False


class IsVendorEmployee(IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR_EMPLOYEE:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor.employee.filter(employee=request.user).exists():
                return True
        return False


class IsVendorOrVendorEmployee(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR or request.user.role == User.Role.VENDOR_EMPLOYEE:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor == request.user or obj.vendor.employee.filter(employee=request.user).exists():
                return True
        return False

