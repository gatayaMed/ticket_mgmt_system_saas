from rest_framework import permissions
from .models import Membership

class IsOrganizationMember(permissions.BasePermission):
    """Check if user is a member of the organization."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('pk')
        if not organization_id:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            organization_id=organization_id,
            is_active=True
        ).exists()

class IsOrganizationAdmin(permissions.BasePermission):
    """Check if user is an admin of the organization."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('pk')
        if not organization_id:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            organization_id=organization_id,
            role=Membership.Role.ADMIN,
            is_active=True
        ).exists()

class IsOrganizationManager(permissions.BasePermission):
    """Check if user is a manager or admin of the organization."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        organization_id = view.kwargs.get('organization_id') or view.kwargs.get('pk')
        if not organization_id:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            organization_id=organization_id,
            role__in=[Membership.Role.ADMIN, Membership.Role.MANAGER],
            is_active=True
        ).exists()

def has_role(user, organization_id, required_roles):
    """Helper function to check if user has required role."""
    if not user.is_authenticated:
        return False
    
    return Membership.objects.filter(
        user=user,
        organization_id=organization_id,
        role__in=required_roles,
        is_active=True
    ).exists()