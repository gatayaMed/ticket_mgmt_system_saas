# projects/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.db.models import Q
from organizations.models import Organization, Membership
from .models import Project, ProjectMember
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer,
    ProjectUpdateSerializer, ProjectMemberSerializer
)

User = get_user_model()

class ProjectListCreateView(generics.ListCreateAPIView):
    """List projects in an organization and create new project."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        organization_id = self.kwargs['organization_id']
        
        # Filter by organization and user permissions
        queryset = Project.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).prefetch_related('project_members', 'project_members__user')
        
        # If user is not admin/manager, only show projects they're a member of
        membership = Membership.objects.filter(
            user=self.request.user,
            organization_id=organization_id,
            is_active=True
        ).first()
        
        if membership and membership.role not in [Membership.Role.ADMIN, Membership.Role.MANAGER]:
            queryset = queryset.filter(
                Q(project_members__user=self.request.user, project_members__is_active=True)
            )
        
        return queryset.distinct()

    def perform_create(self, serializer):
        organization = get_object_or_404(Organization, id=self.kwargs['organization_id'])
        
        # Check if user is admin or manager
        membership = get_object_or_404(
            Membership,
            user=self.request.user,
            organization=organization,
            is_active=True
        )
        
        if membership.role not in [Membership.Role.ADMIN, Membership.Role.MANAGER]:
            raise PermissionDenied("Only admins and managers can create projects.")
        
        project = serializer.save(
            organization=organization,
            created_by=self.request.user
        )
        
        # Auto-generate slug
        if not project.slug:
            base_slug = slugify(project.name)
            project.slug = base_slug
            counter = 1
            while Project.objects.filter(slug=project.slug).exists():
                project.slug = f"{base_slug}-{counter}"
                counter += 1
            project.save()
        
        # Add creator as project lead
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.Role.PROJECT_LEAD
        )

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a project."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectUpdateSerializer
        return ProjectSerializer
    
    def perform_update(self, serializer):
        if 'name' in serializer.validated_data:
            name = serializer.validated_data['name']
            instance = serializer.instance
            new_slug = slugify(name)
            # Check if slug is unique
            if Project.objects.filter(slug=new_slug).exclude(id=instance.id).exists():
                base_slug = new_slug
                counter = 1
                while Project.objects.filter(slug=new_slug).exclude(id=instance.id).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
            serializer.save(slug=new_slug)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

class ProjectMemberListView(generics.ListAPIView):
    """List all members of a project."""
    
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return ProjectMember.objects.filter(
            project_id=project_id,
            is_active=True
        ).select_related('user')

class ProjectMemberAddView(generics.CreateAPIView):
    """Add a member to a project."""
    
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        user_id = request.data.get('user_id')
        role = request.data.get('role', ProjectMember.Role.VIEWER)
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is a member of the organization
        if not Membership.objects.filter(
            user_id=user_id,
            organization=project.organization,
            is_active=True
        ).exists():
            return Response(
                {"error": "User is not a member of this organization"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already a project member
        if ProjectMember.objects.filter(
            project=project,
            user_id=user_id,
            is_active=True
        ).exists():
            return Response(
                {"error": "User is already a member of this project"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        
        membership = ProjectMember.objects.create(
            project=project,
            user=user,
            role=role
        )
        
        serializer = ProjectMemberSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectMemberUpdateView(generics.UpdateAPIView):
    """Update a member's role in a project."""
    
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id or not role:
            return Response(
                {"error": "user_id and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership = get_object_or_404(
            ProjectMember,
            project_id=project_id,
            user_id=user_id,
            is_active=True
        )
        
        if role not in dict(ProjectMember.Role.choices):
            return Response(
                {"error": f"Invalid role. Choices: {', '.join(ProjectMember.Role.choices)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.role = role
        membership.save()
        
        serializer = ProjectMemberSerializer(membership)
        return Response(serializer.data)

class ProjectMemberRemoveView(generics.DestroyAPIView):
    """Remove a member from a project."""
    
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        project_id = self.kwargs['project_id']
        user_id = self.kwargs['user_id']
        
        membership = get_object_or_404(
            ProjectMember,
            project_id=project_id,
            user_id=user_id,
            is_active=True
        )
        
        # Prevent removing the last project lead
        if membership.role == ProjectMember.Role.PROJECT_LEAD:
            lead_count = ProjectMember.objects.filter(
                project_id=project_id,
                role=ProjectMember.Role.PROJECT_LEAD,
                is_active=True
            ).count()
            if lead_count <= 1:
                return Response(
                    {"error": "Cannot remove the last project lead"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        membership.is_active = False
        membership.save()
        
        return Response({"message": "Member removed successfully"}, status=status.HTTP_200_OK)