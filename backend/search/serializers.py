from rest_framework import serializers
from tickets.models import Ticket
from projects.models import Project
from organizations.models import Organization
from accounts.serializers import UserSerializer


class TicketSearchResultSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    assignee_details = UserSerializer(source='assignee', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_id', 'title', 'project', 'project_name',
            'status', 'status_display', 'priority', 'ticket_type',
            'assignee', 'assignee_details', 'due_date', 'updated_at'
        ]


class ProjectSearchResultSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'slug',
                  'organization_name', 'status', 'status_display', 'updated_at']


class OrganizationSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'description']


class GlobalSearchResponseSerializer(serializers.Serializer):
    tickets = TicketSearchResultSerializer(many=True, read_only=True)
    projects = ProjectSearchResultSerializer(many=True, read_only=True)
    organizations = OrganizationSearchResultSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)


class AdvancedTicketSearchSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    priority = serializers.CharField(required=False)
    ticket_type = serializers.CharField(required=False)
    assignee = serializers.IntegerField(required=False)
    project = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False)
    due_date_from = serializers.DateField(required=False)
    due_date_to = serializers.DateField(required=False)
