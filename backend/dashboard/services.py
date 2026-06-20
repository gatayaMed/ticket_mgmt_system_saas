from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket
from projects.models import Project
from organizations.models import Organization

class DashboardService:
    @staticmethod
    def get_overview_stats(user):
        """Get overview statistics for dashboard"""
        organizations = Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        )
        
        projects = Project.objects.filter(
            organization__in=organizations,
            is_active=True
        )
        
        tickets = Ticket.objects.filter(
            project__in=projects,
            is_active=True
        )
        
        return {
            'organizations': organizations.count(),
            'projects': projects.count(),
            'tickets': {
                'total': tickets.count(),
                'todo': tickets.filter(status=Ticket.Status.TODO).count(),
                'in_progress': tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
                'review': tickets.filter(status=Ticket.Status.REVIEW).count(),
                'done': tickets.filter(status=Ticket.Status.DONE).count(),
                'backlog': tickets.filter(status=Ticket.Status.BACKLOG).count(),
            },
            'tickets_by_priority': {
                'critical': tickets.filter(priority=Ticket.Priority.CRITICAL).count(),
                'high': tickets.filter(priority=Ticket.Priority.HIGH).count(),
                'medium': tickets.filter(priority=Ticket.Priority.MEDIUM).count(),
                'low': tickets.filter(priority=Ticket.Priority.LOW).count(),
            },
            'tickets_by_type': {
                'bug': tickets.filter(ticket_type=Ticket.Type.BUG).count(),
                'feature': tickets.filter(ticket_type=Ticket.Type.FEATURE).count(),
                'task': tickets.filter(ticket_type=Ticket.Type.TASK).count(),
                'improvement': tickets.filter(ticket_type=Ticket.Type.IMPROVEMENT).count(),
            },
            'overdue': tickets.filter(
                due_date__lt=timezone.now(),
                status__in=[Ticket.Status.BACKLOG, Ticket.Status.TODO, Ticket.Status.IN_PROGRESS]
            ).count(),
            'completed_this_week': tickets.filter(
                completed_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
        }

    @staticmethod
    def get_project_stats(project_id):
        """Get detailed statistics for a project"""
        tickets = Ticket.objects.filter(project_id=project_id, is_active=True)
        
        # Burndown data
        burndown = []
        for days_ago in range(14, -1, -1):
            date = timezone.now() - timedelta(days=days_ago)
            completed = tickets.filter(
                status=Ticket.Status.DONE,
                completed_at__date=date.date()
            ).count()
            burndown.append({
                'date': date.date().isoformat(),
                'completed': completed
            })
        
        return {
            'total_tickets': tickets.count(),
            'completion_rate': DashboardService._calculate_completion_rate(tickets),
            'average_completion_time': DashboardService._calculate_avg_completion_time(tickets),
            'burndown': burndown,
            'velocity': DashboardService._calculate_velocity(project_id),
        }

    @staticmethod
    def _calculate_completion_rate(tickets):
        total = tickets.count()
        if total == 0:
            return 0
        done = tickets.filter(status=Ticket.Status.DONE).count()
        return int((done / total) * 100)

    @staticmethod
    def _calculate_avg_completion_time(tickets):
        completed = tickets.filter(
            status=Ticket.Status.DONE,
            completed_at__isnull=False
        )
        if not completed.exists():
            return None
        
        total_days = 0
        for ticket in completed:
            days = (ticket.completed_at - ticket.created_at).days
            total_days += days
        
        return total_days / completed.count()

    @staticmethod
    def _calculate_velocity(project_id):
        """Calculate team velocity (average tickets completed per sprint)"""
        from sprints.models import Sprint
        sprints = Sprint.objects.filter(
            project_id=project_id,
            status=Sprint.Status.COMPLETED
        )
        
        if not sprints.exists():
            return 0
        
        total_completed = sum(sprint.tickets.filter(
            status=Ticket.Status.DONE
        ).count() for sprint in sprints)
        
        return int(total_completed / sprints.count())