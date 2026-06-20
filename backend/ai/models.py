from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from tickets.models import Ticket
from projects.models import ProjectMember


class DeveloperProfile(models.Model):
    """Developer profile with skills and performance metrics."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='developer_profile'
    )

    # Skills
    skills = models.JSONField(default=dict, blank=True)
    years_experience = models.IntegerField(default=0)

    # Performance metrics
    avg_resolution_time = models.FloatField(null=True, blank=True)
    success_rate = models.FloatField(null=True, blank=True)
    tickets_completed = models.IntegerField(default=0)
    avg_rating = models.FloatField(null=True, blank=True)

    # Workload
    current_workload = models.IntegerField(default=0)
    max_workload = models.IntegerField(default=5)
    is_available = models.BooleanField(default=True)
    last_active = models.DateTimeField(null=True, blank=True)

    # AI learning
    suggestion_accuracy = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'developer_profiles'

    def __str__(self):
        return f"Profile: {self.user.username}"


class AIAssignmentSuggestion(models.Model):
    """AI suggestions for ticket assignment (manager approval workflow)."""

    STATUS_CHOICES = [
        ('pending', 'Pending Manager Review'),
        ('approved', 'Approved by Manager'),
        ('rejected', 'Rejected by Manager'),
        ('modified', 'Modified by Manager'),
        ('expired', 'Expired'),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='ai_suggestions'
    )

    # Suggested developers (ranked)
    suggestions = models.JSONField()  # List of {user_id, score, reasoning, breakdown}

    # Criteria used
    criteria_used = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Manager action
    manager_approved_choice = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_suggestions'
    )
    manager_notes = models.TextField(null=True, blank=True)

    # Feedback loop
    feedback_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_assignment_suggestions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion for {self.ticket.ticket_id} ({self.status})"


class AssignmentHistory(models.Model):
    """Track every assignment for AI learning."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )
    suggested_by_ai = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggested_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='approved_assignments'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_assignments'
    )

    # Status
    was_ai_suggestion = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)
    manager_approved = models.BooleanField(default=True)

    # Reasoning
    ai_reasoning = models.TextField(null=True, blank=True)
    manager_notes = models.TextField(null=True, blank=True)

    # Learning
    was_successful = models.BooleanField(default=True)
    resolution_time = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignment_history'
        ordering = ['-created_at']


class AICache(models.Model):
    """Cache for AI responses (persistent fallback when Redis is unavailable)."""

    key = models.CharField(max_length=255, unique=True)
    response = models.JSONField()
    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'ai_cache'

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class AIMetrics(models.Model):
    """Track AI usage and performance."""

    provider = models.CharField(max_length=50)
    endpoint = models.CharField(max_length=100)
    request_time = models.FloatField()
    tokens_used = models.IntegerField(default=0)
    success = models.BooleanField(default=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_metrics'
        ordering = ['-created_at']

    @classmethod
    def record(cls, provider, endpoint, request_time, tokens=0, success=True, error=None):
        return cls.objects.create(
            provider=provider,
            endpoint=endpoint,
            request_time=request_time,
            tokens_used=tokens,
            success=success,
            error=error
        )

    @classmethod
    def get_stats(cls, hours=24):
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Sum, Count

        cutoff = timezone.now() - timedelta(hours=hours)
        qs = cls.objects.filter(created_at__gte=cutoff)
        total = qs.count()
        if total == 0:
            return {'total_requests': 0, 'success_rate': 0, 'avg_response_time': 0, 'total_tokens': 0}

        success_count = qs.filter(success=True).count()
        return {
            'total_requests': total,
            'success_rate': round((success_count / total) * 100, 1),
            'avg_response_time': round(qs.aggregate(avg=Avg('request_time'))['avg'] or 0, 3),
            'total_tokens': qs.aggregate(total=Sum('tokens_used'))['total'] or 0,
        }
