from rest_framework import serializers
from .models import Webhook, WebhookLog


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = [
            'id', 'organization', 'name', 'url', 'events',
            'is_active', 'last_triggered', 'failure_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'secret', 'last_triggered',
                           'last_response', 'failure_count', 'created_at', 'updated_at']


class WebhookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = ['name', 'url', 'events', 'is_active']


class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = ['id', 'webhook', 'event', 'payload', 'response_status',
                  'response_body', 'duration', 'created_at']
        read_only_fields = ['id', 'created_at']
