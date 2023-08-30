from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User


class IsCustomer(IsAuthenticated):

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if request.user.role == User.Role.CUSTOMER:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            if obj.customer == request.user:
                return True
        return False
