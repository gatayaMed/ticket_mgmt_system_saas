from django.db import models
from django.conf import settings
from django.utils import timezone
import hmac
import hashlib
import secrets

class Webhook(models.Model):
    class Event(models.TextChoices):
        TICKET_CREATED = 'ticket.created', 'Ticket Created'
        TICKET_UPDATED = 'ticket.updated', 'Ticket Updated'
        TICKET_STATUS_CHANGED = 'ticket.status_changed', 'Ticket Status Changed'
        TICKET_ASSIGNED = 'ticket.assigned', 'Ticket Assigned'
        COMMENT_ADDED = 'comment.added', 'Comment Added'
        PROJECT_CREATED = 'project.created', 'Project Created'
        PROJECT_UPDATED = 'project.updated', 'Project Updated'
        SPRINT_STARTED = 'sprint.started', 'Sprint Started'
        SPRINT_COMPLETED = 'sprint.completed', 'Sprint Completed'

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='webhooks'
    )
    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(default=list)  # List of event types
    secret = models.CharField(max_length=64, default=secrets.token_urlsafe)
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_response = models.JSONField(null=True, blank=True)
    failure_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhooks'

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    def generate_signature(self, payload):
        """Generate HMAC signature for webhook payload"""
        return hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

class WebhookLog(models.Model):
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    event = models.CharField(max_length=50)
    payload = models.JSONField()
    response_status = models.IntegerField()
    response_body = models.TextField(blank=True, null=True)
    duration = models.FloatField()  # Response time in seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_logs'
        ordering = ['-created_at']