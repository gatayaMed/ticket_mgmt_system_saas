# projects/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from organizations.models import Organization
from django.core.validators import MinValueValidator, MaxValueValidator 
class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        COMPLETED = 'completed', 'Completed'
        ARCHIVED = 'archived', 'Archived'
        ON_HOLD = 'on_hold', 'On Hold'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects'
    )
    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='projects'
    )
    
    # Progress tracking
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        unique_together = ['organization', 'slug']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class ProjectMember(models.Model):
    class Role(models.TextChoices):
        PROJECT_LEAD = 'project_lead', 'Project Lead'
        DEVELOPER = 'developer', 'Developer'
        QA = 'qa', 'QA'
        VIEWER = 'viewer', 'Viewer'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_members'
        unique_together = ['project', 'user']
        ordering = ['-joined_at']
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'

    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.role})"