from rest_framework import serializers
from .models import (
    DeveloperProfile, AIAssignmentSuggestion, AssignmentHistory, AIMetrics
)


class DeveloperProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DeveloperProfile
        fields = [
            'id', 'user', 'username', 'skills', 'years_experience',
            'avg_resolution_time', 'success_rate', 'tickets_completed',
            'avg_rating', 'current_workload', 'max_workload',
            'is_available', 'last_active', 'suggestion_accuracy',
        ]
        read_only_fields = ['id', 'user', 'suggestion_accuracy']


class AIAssignmentSuggestionSerializer(serializers.ModelSerializer):
    ticket_code = serializers.CharField(source='ticket.ticket_id', read_only=True)
    ticket_title = serializers.CharField(source='ticket.title', read_only=True)

    class Meta:
        model = AIAssignmentSuggestion
        fields = [
            'id', 'ticket', 'ticket_code', 'ticket_title',
            'suggestions', 'criteria_used', 'status',
            'manager_approved_choice', 'manager_notes',
            'feedback_score', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssignmentHistorySerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = AssignmentHistory
        fields = [
            'id', 'ticket', 'assigned_by', 'assigned_by_name',
            'assigned_to', 'assigned_to_name',
            'was_ai_suggestion', 'ai_confidence', 'manager_approved',
            'ai_reasoning', 'manager_notes',
            'was_successful', 'resolution_time', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AIMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMetrics
        fields = ['id', 'provider', 'endpoint', 'request_time',
                  'tokens_used', 'success', 'error', 'created_at']
        read_only_fields = ['id', 'created_at']


# Request serializers
class ClassifyRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)


class PredictPriorityRequestSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)


class ApproveRequestSerializer(serializers.Serializer):
    suggestion_id = serializers.IntegerField(required=True)
    user_id = serializers.IntegerField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class RejectRequestSerializer(serializers.Serializer):
    suggestion_id = serializers.IntegerField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
