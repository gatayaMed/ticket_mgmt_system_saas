# projects/serializers.py
from rest_framework import serializers
from django.utils.text import slugify
from .models import Project, ProjectMember
from organizations.serializers import OrganizationSerializer
from accounts.serializers import UserSerializer
from django.utils import timezone

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = [
            'id', 'user', 'user_email', 'user_username', 'user_details',
            'role', 'role_display', 'is_active', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']

class ProjectSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'slug', 'organization', 'organization_name',
            'status', 'status_display', 'priority', 'priority_display',
            'start_date', 'end_date', 'due_date',
            'created_by', 'created_by_email', 'created_by_username',
            'created_at', 'updated_at', 'is_active', 'progress',
            'member_count', 'is_overdue', 'days_remaining'
        ]
        read_only_fields = ['id', 'slug', 'created_by', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.project_members.filter(is_active=True).count()
    
    def get_is_overdue(self, obj):
        if obj.due_date:

            return obj.due_date < timezone.now() and obj.status != Project.Status.COMPLETED
        return False
    
    def get_days_remaining(self, obj):
        if obj.due_date:

            delta = obj.due_date - timezone.now()
            return delta.days
        return None

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'priority',
            'start_date', 'end_date', 'due_date'
        ]
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Project name must be at least 3 characters long.")
        return value
    
    def validate(self, data):
        # Validate dates
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({
                    "end_date": "End date must be after start date."
                })
        
        if data.get('start_date') and data.get('due_date'):
            if data['start_date'] > data['due_date']:
                raise serializers.ValidationError({
                    "due_date": "Due date must be after start date."
                })
        
        return data

class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'priority',
            'start_date', 'end_date', 'due_date', 'progress'
        ]
    
    def validate_progress(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress must be between 0 and 100.")
        return value