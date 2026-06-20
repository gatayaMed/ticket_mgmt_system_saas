# notifications/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from tickets.models import Ticket

class Notification(models.Model):
    class Type(models.TextChoices):
        TICKET_CREATED = 'ticket_created', 'Ticket Created'
        TICKET_UPDATED = 'ticket_updated', 'Ticket Updated'
        TICKET_ASSIGNED = 'ticket_assigned', 'Ticket Assigned'
        TICKET_STATUS_CHANGED = 'ticket_status_changed', 'Ticket Status Changed'
        COMMENT_ADDED = 'comment_added', 'Comment Added'
        MENTION = 'mention', 'Mention'
        TICKET_DUE = 'ticket_due', 'Ticket Due'
        TICKET_OVERDUE = 'ticket_overdue', 'Ticket Overdue'
        PROJECT_CREATED = 'project_created', 'Project Created'
        MEMBER_ADDED = 'member_added', 'Member Added'

    class Channel(models.TextChoices):
        EMAIL = 'email', 'Email'
        SLACK = 'slack', 'Slack'
        IN_APP = 'in_app', 'In-App'
        ALL = 'all', 'All'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.IN_APP)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

class NotificationPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    email_enabled = models.BooleanField(default=True)
    slack_enabled = models.BooleanField(default=False)
    slack_webhook_url = models.URLField(blank=True, null=True)
    ticket_created = models.BooleanField(default=True)
    ticket_assigned = models.BooleanField(default=True)
    ticket_status_changed = models.BooleanField(default=True)
    comment_added = models.BooleanField(default=True)
    mentions = models.BooleanField(default=True)
    ticket_due_reminders = models.BooleanField(default=True)
    daily_digest = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"