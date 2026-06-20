from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'type', 'type_display', 'channel', 'channel_display',
            'title', 'message', 'link', 'is_read',
            'metadata', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'read_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user',
            'email_enabled', 'slack_enabled', 'slack_webhook_url',
            'ticket_created', 'ticket_assigned', 'ticket_status_changed',
            'comment_added', 'mentions', 'ticket_due_reminders',
            'daily_digest', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
