from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project
from tickets.models import Ticket

class Sprint(models.Model):
    class Status(models.TextChoices):
        PLANNING = 'planning', 'Planning'
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='sprints'
    )
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING
    )
    tickets = models.ManyToManyField(
        Ticket,
        related_name='sprints',
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sprints'
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sprints'
        ordering = ['-start_date']
        unique_together = ['project', 'name']

    def __str__(self):
        return f"{self.project.name} - {self.name}"

    @property
    def progress(self):
        total = self.tickets.count()
        if total == 0:
            return 0
        done = self.tickets.filter(status=Ticket.Status.DONE).count()
        return int((done / total) * 100)

    @property
    def total_points(self):
        return self.tickets.aggregate(
            total=models.Sum('estimated_hours')
        )['total'] or 0

    @property
    def completed_points(self):
        return self.tickets.filter(
            status=Ticket.Status.DONE
        ).aggregate(
            total=models.Sum('estimated_hours')
        )['total'] or 0

class SprintHistory(models.Model):
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sprint_history'
        ordering = ['-created_at']