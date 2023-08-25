from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User


class IsVendor(IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.vendor == request.user or obj.vendor.vendor == request.user:
                return True
        return False


class IsVendorEmployee(IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.VENDOR_EMPLOYEE:
                return True
        return False
