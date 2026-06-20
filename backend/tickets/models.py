from django.db import models
from django.conf import settings
from django.utils import timezone
from organizations.models import Organization
from projects.models import Project
from django.core.validators import MinValueValidator, MaxValueValidator 
class Ticket(models.Model):
    class Status(models.TextChoices):
        BACKLOG = 'backlog', 'Backlog'
        TODO = 'todo', 'Todo'
        IN_PROGRESS = 'in_progress', 'In Progress'
        REVIEW = 'review', 'Review'
        DONE = 'done', 'Done'
        CLOSED = 'closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    class Type(models.TextChoices):
        BUG = 'bug', 'Bug'
        FEATURE = 'feature', 'Feature'
        TASK = 'task', 'Task'
        IMPROVEMENT = 'improvement', 'Improvement'
        EPIC = 'epic', 'Epic'

    # Core fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    ticket_id = models.CharField(max_length=20, unique=True, blank=True)
    estimated_hours = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]  # ADD VALIDATORS
    )
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    
    # Status & Priority
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    ticket_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.TASK
    )
    
    # Assignment
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tickets'
    )
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate ticket ID: PRJ-001, PRJ-002, etc.
            prefix = self.project.name[:4].upper()
            last_ticket = Ticket.objects.filter(
                project=self.project
            ).order_by('-id').first()
            
            if last_ticket and last_ticket.ticket_id:
                try:
                    last_num = int(last_ticket.ticket_id.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.ticket_id = f"{prefix}-{new_num:03d}"
        
        # Auto-complete logic
        if self.status == self.Status.DONE and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != self.Status.DONE:
            self.completed_at = None
        
        super().save(*args, **kwargs)

class TicketHistory(models.Model):
    """Track changes to tickets"""
    
    class Action(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        ASSIGNED = 'assigned', 'Assigned'
        PRIORITY_CHANGED = 'priority_changed', 'Priority Changed'
        COMMENTED = 'commented', 'Commented'
        ATTACHMENT_ADDED = 'attachment_added', 'Attachment Added'

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ticket_actions'
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ticket_history'
        ordering = ['-created_at']
        verbose_name = 'Ticket History'
        verbose_name_plural = 'Ticket Histories'

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.action} by {self.user.email if self.user else 'System'}"