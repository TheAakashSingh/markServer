import jwt
import logging
from rest_framework import permissions

from user_management.models import UserProfile, UserRoles

logger = logging.getLogger(__name__)

class IsAdmin(permissions.BasePermission):
    allowed_roles = ["Admin"]

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return str(request.user.role) in self.allowed_roles
        
class IsModerator(permissions.BasePermission):
    allowed_roles = ["Admin", "Moderator"]
    def has_permission(self, request, view):
        return str(request.user.role) in self.allowed_roles
    
class IsUser(permissions.BasePermission):
    allowed_roles = ["Admin", "Moderator", "User"]

    def has_permission(self, request, view):
        return str(request.user.role) in self.allowed_roles

class IsSelfOrAdmin(permissions.BasePermission):
    allowed_roles = ["Admin"]    

    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id or str(request.user.role) in self.allowed_roles