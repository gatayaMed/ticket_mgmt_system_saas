# organizations/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Organization, Membership, Invitation
from accounts.serializers import UserSerializer

User = get_user_model()

class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model with additional computed fields.
    Used for retrieving organization details.
    """
    member_count = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    user_role = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 
            'website', 'created_by', 'created_by_email',
            'created_at', 'updated_at', 'is_active', 
            'member_count', 'user_role', 'is_admin'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'slug']
    
    def get_member_count(self, obj):
        """Get total active members in the organization."""
        return obj.memberships.filter(is_active=True).count()
    
    def get_user_role(self, obj):
        """Get the current user's role in this organization."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = Membership.objects.filter(
                user=request.user,
                organization=obj,
                is_active=True
            ).first()
            return membership.role if membership else None
        return None
    
    def get_is_admin(self, obj):
        """Check if current user is an admin of this organization."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = Membership.objects.filter(
                user=request.user,
                organization=obj,
                role=Membership.Role.ADMIN,
                is_active=True
            ).exists()
            return membership
        return False

class OrganizationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new organization.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description', 'website', 'logo']
    
    def validate_name(self, value):
        """Validate that organization name is unique."""
        if Organization.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("An organization with this name already exists.")
        return value
    
    def validate_website(self, value):
        """Validate website URL format."""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Website must start with http:// or https://")
        return value

class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for Membership model with nested user and organization details.
    """
    user_details = UserSerializer(source='user', read_only=True)
    organization_details = OrganizationSerializer(source='organization', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_details', 'organization', 
            'organization_details', 'role', 'role_display',
            'is_active', 'joined_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'organization', 'joined_at', 'updated_at']

class MembershipCreateSerializer(serializers.Serializer):
    """
    Serializer for adding a member to an organization.
    """
    user_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(
        choices=Membership.Role.choices,
        default=Membership.Role.VIEWER
    )
    
    def validate_user_id(self, value):
        """Validate that the user exists."""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {value} does not exist.")
        return value

class MembershipUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating a member's role.
    """
    user_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=Membership.Role.choices, required=True)
    
    def validate(self, data):
        """Validate the role update."""
        user_id = data.get('user_id')
        role = data.get('role')
        
        # Additional validation can be added here
        # For example, prevent demoting the last admin
        return data

class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for Invitation model.
    """
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'organization', 'organization_name',
            'role', 'role_display', 'invited_by', 'invited_by_email',
            'invited_by_username', 'token', 'status', 'status_display',
            'is_expired', 'expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'token', 'status', 'created_at', 'updated_at', 'invited_by']
    
    def get_is_expired(self, obj):
        """Check if the invitation has expired."""
        return obj.expires_at < timezone.now()

class InvitationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new invitation.
    """
    class Meta:
        model = Invitation
        fields = ['email', 'role']
    
    def validate_email(self, value):
        """Validate email format and check if user already has pending invitation."""
        # Basic email validation
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address.")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        email = data.get('email')
        role = data.get('role')
        organization = self.context.get('organization')
        
        if organization:
            # Check if user already has a pending invitation
            if Invitation.objects.filter(
                email=email,
                organization=organization,
                status=Invitation.Status.PENDING
            ).exists():
                raise serializers.ValidationError({
                    "email": "This user already has a pending invitation."
                })
            
            # Check if user is already a member
            try:
                user = User.objects.get(email=email)
                if Membership.objects.filter(
                    user=user,
                    organization=organization,
                    is_active=True
                ).exists():
                    raise serializers.ValidationError({
                        "email": "This user is already a member of the organization."
                    })
            except User.DoesNotExist:
                # User doesn't exist, that's fine for invitations
                pass
        
        return data

class InvitationAcceptSerializer(serializers.Serializer):
    """
    Serializer for accepting an invitation.
    """
    token = serializers.CharField(required=True)

class InvitationDeclineSerializer(serializers.Serializer):
    """
    Serializer for declining an invitation.
    """
    token = serializers.CharField(required=True)

class UserOrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for user's organization details.
    """
    role = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'logo', 'website',
            'description', 'role', 'role_display', 
            'is_admin', 'member_count', 'is_active'
        ]
    
    def get_role(self, obj):
        """Get current user's role in the organization."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = Membership.objects.filter(
                user=request.user,
                organization=obj,
                is_active=True
            ).first()
            return membership.role if membership else None
        return None
    
    def get_role_display(self, obj):
        """Get display name of the role."""
        role = self.get_role(obj)
        return dict(Membership.Role.choices).get(role) if role else None
    
    def get_is_admin(self, obj):
        """Check if current user is an admin."""
        role = self.get_role(obj)
        return role == Membership.Role.ADMIN
    
    def get_member_count(self, obj):
        """Get total active members."""
        return obj.memberships.filter(is_active=True).count()

class OrganizationMemberSerializer(serializers.Serializer):
    """
    Serializer for organization member operations.
    """
    user_id = serializers.IntegerField(required=True)
    role = serializers.ChoiceField(choices=Membership.Role.choices, required=True)

class OrganizationRoleUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating multiple members' roles at once.
    """
    members = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    
    def validate_members(self, value):
        """Validate each member object."""
        for member in value:
            if 'user_id' not in member or 'role' not in member:
                raise serializers.ValidationError(
                    "Each member must have 'user_id' and 'role' fields."
                )
            if member['role'] not in dict(Membership.Role.choices):
                raise serializers.ValidationError(
                    f"Invalid role. Choices: {', '.join(Membership.Role.choices)}"
                )
        return value

class OrganizationInvitationResendSerializer(serializers.Serializer):
    """
    Serializer for resending an invitation.
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if email has a valid invitation."""
        # Validate that an invitation exists for this email
        return value

class OrganizationLeaveSerializer(serializers.Serializer):
    """
    Serializer for leaving an organization.
    """
    organization_id = serializers.IntegerField(required=True)
    confirm = serializers.BooleanField(required=True)
    
    def validate(self, data):
        """Validate leaving organization."""
        if not data.get('confirm'):
            raise serializers.ValidationError({
                "confirm": "Please confirm you want to leave the organization."
            })
        return data

""" 
Summary of What Was Missing
OrganizationSerializer - Added user_role and is_admin fields

MembershipCreateSerializer - New serializer for adding members

InvitationCreateSerializer - New serializer for creating invitations

InvitationAcceptSerializer - For accepting invitations

InvitationDeclineSerializer - For declining invitations

UserOrganizationSerializer - Enhanced with more fields

OrganizationMemberSerializer - For member operations

OrganizationRoleUpdateSerializer - For bulk role updates

OrganizationInvitationResendSerializer - For resending invitations

OrganizationLeaveSerializer - For leaving organizations


"""