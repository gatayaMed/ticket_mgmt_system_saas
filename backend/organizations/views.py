from rest_framework import generics, permissions, status, serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

import secrets
from .models import Organization, Membership, Invitation
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    MembershipSerializer, MembershipUpdateSerializer,
    InvitationSerializer,InvitationAcceptSerializer,InvitationAcceptSerializer, InvitationDeclineSerializer 
)
from .permissions import IsOrganizationAdmin, IsOrganizationManager, IsOrganizationMember
from accounts.serializers import UserSerializer

User = get_user_model() 

class OrganizationListCreateView(generics.ListCreateAPIView):
    """List all organizations user belongs to and create new organization."""
    
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return organizations where user is a member
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True,
            is_active=True
        ).distinct()

    def perform_create(self, serializer):
        # Create organization and add user as admin
        organization = serializer.save(created_by=self.request.user)
        
        # Auto-generate slug if not provided
        if not organization.slug:
            organization.slug = slugify(organization.name)
            # Ensure unique slug
            base_slug = organization.slug
            counter = 1
            while Organization.objects.filter(slug=organization.slug).exists():
                organization.slug = f"{base_slug}-{counter}"
                counter += 1
            organization.save()
        
        # Add creator as admin
        Membership.objects.create(
            user=self.request.user,
            organization=organization,
            role=Membership.Role.ADMIN,
            invited_by=self.request.user
        )

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an organization."""
    
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def perform_update(self, serializer):
        if 'name' in serializer.validated_data:
            name = serializer.validated_data['name']
            serializer.save(slug=slugify(name))
        else:
            serializer.save()

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

class OrganizationMemberListView(generics.ListAPIView):
    """List all members of an organization."""
    
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        organization_id = self.kwargs['organization_id']
        return Membership.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).select_related('user')


class OrganizationMemberAddView(generics.CreateAPIView):
    """Add a member to an organization."""
    
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def create(self, request, *args, **kwargs):
        organization_id = kwargs['organization_id']
        user_id = request.data.get('user_id')
        role = request.data.get('role', Membership.Role.VIEWER)
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        organization = get_object_or_404(Organization, id=organization_id)
        
        # Check if user is already a member
        if Membership.objects.filter(user=user, organization=organization, is_active=True).exists():
            return Response(
                {"error": "User is already a member of this organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in dict(Membership.Role.choices):
            return Response(
                {"error": "Invalid role. Choices: admin, manager, developer, support, viewer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = Membership.objects.create(
            user=user,
            organization=organization,
            role=role,
            invited_by=request.user
        )
        
        serializer = MembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrganizationMemberUpdateView(generics.UpdateAPIView):
    """Update a member's role in an organization."""
    
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def update(self, request, *args, **kwargs):
        organization_id = kwargs['organization_id']
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id or not role:
            return Response(
                {"error": "user_id and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in dict(Membership.Role.choices):
            return Response(
                {"error": f"Invalid role. Choices: {', '.join(Membership.Role.choices)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            membership = Membership.objects.get(
                organization_id=organization_id,
                user_id=user_id,
                is_active=True
            )
        except Membership.DoesNotExist:
            return Response(
                {"error": "User is not a member of this organization"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prevent removing the last admin
        if membership.role == Membership.Role.ADMIN and role != Membership.Role.ADMIN:
            admin_count = Membership.objects.filter(
                organization_id=organization_id,
                role=Membership.Role.ADMIN,
                is_active=True
            ).count()
            if admin_count <= 1:
                return Response(
                    {"error": "Cannot remove the last admin of the organization"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        membership.role = role
        membership.save()
        
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)

class OrganizationMemberRemoveView(generics.DestroyAPIView):
    """Remove a member from an organization."""
    
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def destroy(self, request, *args, **kwargs):
        organization_id = kwargs['organization_id']
        user_id = kwargs['user_id']
        
        membership = get_object_or_404(
            Membership,
            organization_id=organization_id,
            user_id=user_id,
            is_active=True
        )
        
        # Prevent removing the last admin
        if membership.role == Membership.Role.ADMIN:
            admin_count = Membership.objects.filter(
                organization_id=organization_id,
                role=Membership.Role.ADMIN,
                is_active=True
            ).count()
            if admin_count <= 1:
                return Response(
                    {"error": "Cannot remove the last admin of the organization"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Soft delete
        membership.is_active = False
        membership.save()
        
        return Response({"message": "Member removed successfully"}, status=status.HTTP_200_OK)
    

  


class InvitationListView(generics.ListAPIView):
    """List all invitations for an organization."""
    
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationManager]

    def get_queryset(self):
        organization_id = self.kwargs['organization_id']
        return Invitation.objects.filter(
            organization_id=organization_id
        ).order_by('-created_at')

class InvitationCreateView(generics.CreateAPIView):
    """Invite a user to an organization."""
    
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def create(self, request, *args, **kwargs):
        organization_id = self.kwargs['organization_id']
        organization = get_object_or_404(Organization, id=organization_id)
        
        email = request.data.get('email')
        role = request.data.get('role', Membership.Role.VIEWER)
        
        if not email:
            return Response(
                {"error": "email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if role not in dict(Membership.Role.choices):
            return Response(
                {"error": f"Invalid role. Choices: {', '.join(Membership.Role.choices)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has a pending invitation
        if Invitation.objects.filter(
            email=email,
            organization=organization,
            status=Invitation.Status.PENDING
        ).exists():
            return Response(
                {"error": "User already has a pending invitation"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already a member
        try:
            user = User.objects.get(email=email)
            if Membership.objects.filter(
                user=user,
                organization=organization,
                is_active=True
            ).exists():
                return Response(
                    {"error": "User is already a member of this organization"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            # User doesn't exist, that's fine
            pass
        
        # Generate token
        token = secrets.token_urlsafe(32)
        
        # Create invitation
        invitation = Invitation.objects.create(
            email=email,
            organization=organization,
            role=role,
            invited_by=request.user,
            token=token,
            expires_at=timezone.now() + timedelta(days=7),
            status=Invitation.Status.PENDING
        )
        
        # Optional: Send email notification (commented out for now)
        # try:
        #     send_invitation_email(invitation, request)
        # except Exception as e:
        #     print(f"Failed to send invitation email: {e}")
        
        serializer = InvitationSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class InvitationAcceptView(generics.GenericAPIView):
    """Accept an invitation to join an organization."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = InvitationAcceptSerializer
    
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invitation = Invitation.objects.get(token=token, status=Invitation.Status.PENDING)
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invalid or expired invitation"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if invitation is expired
        if invitation.expires_at < timezone.now():
            invitation.status = Invitation.Status.EXPIRED
            invitation.save()
            return Response(
                {"error": "Invitation has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user exists
        try:
            user = User.objects.get(email=invitation.email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist. Please register first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already a member
        if Membership.objects.filter(user=user, organization=invitation.organization, is_active=True).exists():
            invitation.status = Invitation.Status.ACCEPTED
            invitation.save()
            return Response(
                {"message": "User is already a member of this organization"},
                status=status.HTTP_200_OK
            )
        
        # Create membership
        Membership.objects.create(
            user=user,
            organization=invitation.organization,
            role=invitation.role,
            invited_by=invitation.invited_by
        )
        
        invitation.status = Invitation.Status.ACCEPTED
        invitation.save()
        
        return Response({
            "message": "Invitation accepted successfully",
            "organization": OrganizationSerializer(invitation.organization).data,
            "role": invitation.role
        }, status=status.HTTP_200_OK)

class InvitationDeclineView(generics.GenericAPIView):
    """Decline an invitation to join an organization."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = InvitationDeclineSerializer

    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            invitation = Invitation.objects.get(token=token, status=Invitation.Status.PENDING)
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invalid invitation"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        invitation.status = Invitation.Status.DECLINED
        invitation.save()
        
        return Response({
            "message": "Invitation declined successfully"
        }, status=status.HTTP_200_OK)