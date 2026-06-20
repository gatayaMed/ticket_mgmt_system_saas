from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from organizations.models import Organization

class Activity(models.Model):
    class Action(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        DELETED = 'deleted', 'Deleted'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        ASSIGNED = 'assigned', 'Assigned'
        COMMENTED = 'commented', 'Commented'
        ATTACHED = 'attached', 'Attached'
        COMPLETED = 'completed', 'Completed'
        MOVED = 'moved', 'Moved'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='activities',
        null=True
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    description = models.TextField()
    # Generic relation for the object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

class ActivityFeed:
    @staticmethod
    def create_activity(user, action, description, organization=None, content_object=None, metadata=None):
        """Create a new activity entry"""
        activity = Activity(
            user=user,
            action=action,
            description=description,
            organization=organization,
            content_object=content_object,
            metadata=metadata or {}
        )
        activity.save()
        return activity

    @staticmethod
    def get_feed(user, limit=50, offset=0):
        """Get activity feed for a user"""
        # Get activities from user's organizations
        org_ids = Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).values_list('id', flat=True)
        
        return Activity.objects.filter(
            Q(organization_id__in=org_ids) |
            Q(user=user)
        ).select_related('user', 'content_type')[:limit]

    @staticmethod
    def get_entity_feed(content_object, limit=50):
        """Get activity feed for a specific entity (ticket, project, etc.)"""
        return Activity.objects.filter(
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.id
        ).select_related('user')[:limit]