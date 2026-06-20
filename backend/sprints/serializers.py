from rest_framework import serializers
from .models import Sprint, SprintHistory
from accounts.serializers import UserSerializer


class SprintSerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    ticket_count = serializers.SerializerMethodField()
    progress = serializers.IntegerField(read_only=True)
    total_points = serializers.FloatField(read_only=True)
    completed_points = serializers.FloatField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sprint
        fields = [
            'id', 'project', 'name', 'goal',
            'start_date', 'end_date', 'status', 'status_display',
            'created_by', 'created_by_details',
            'ticket_count', 'progress', 'total_points', 'completed_points',
            'completed_at', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'completed_at', 'created_at', 'updated_at']

    def get_ticket_count(self, obj):
        return obj.tickets.count()


class SprintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name', 'goal', 'start_date', 'end_date', 'status']

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })
        return data


class SprintHistorySerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = SprintHistory
        fields = ['id', 'action', 'description', 'user', 'user_details', 'created_at']
        read_only_fields = ['id', 'created_at']
