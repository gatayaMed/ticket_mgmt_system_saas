# tickets/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Ticket, TicketHistory
from accounts.serializers import UserSerializer

class TicketHistorySerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = TicketHistory
        fields = [
            'id', 'action', 'description', 'old_value', 'new_value',
            'user', 'user_details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    assignee_details = UserSerializer(source='assignee', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'title', 'description',
            'project', 'project_name', 'organization', 'organization_name',
            'status', 'status_display', 'priority', 'priority_display',
            'ticket_type', 'type_display',
            'assignee', 'assignee_details',
            'created_by', 'created_by_details',
            'due_date', 'estimated_hours', 'completed_at',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ticket_id', 'created_by', 'created_at', 'updated_at', 'completed_at']

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'title', 'description',  # REMOVED project and organization from here
            'status', 'priority', 'ticket_type',
            'assignee', 'due_date', 'estimated_hours'
        ]

    def validate(self, data):
        # Get project and organization from context
        project = self.context.get('project')
        organization = self.context.get('organization')
        
        if not project or not organization:
            raise serializers.ValidationError(
                "Project and organization must be provided in context."
            )
        
        if data.get('assignee'):
            from projects.models import ProjectMember
            if not ProjectMember.objects.filter(
                project=project,
                user=data['assignee'],
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    "Assignee must be a member of the project."
                )
        
        # Check due date is not in the past
        if data.get('due_date') and data['due_date'] < timezone.now():
            raise serializers.ValidationError({
                "due_date": "Due date cannot be in the past."
            })
        
        return data

class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'title', 'description', 'status', 'priority',
            'ticket_type', 'assignee', 'due_date', 'estimated_hours'
        ]