"""
Custom permissions for accounts app.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the object.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class IsWaiter(permissions.BasePermission):
    """
    Permission to check if user is a waiter.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_waiter


class IsRestaurantOwner(permissions.BasePermission):
    """
    Permission to check if user is restaurant owner.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_owner


class IsRestaurantStaff(permissions.BasePermission):
    """
    Permission to check if user works in restaurant.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_owner or request.user.is_waiter
        )


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission to check if user is superadmin.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superadmin
