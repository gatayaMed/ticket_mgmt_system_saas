from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket


class BurndownService:
    @staticmethod
    def calculate_burndown(sprint):
        """Calculate burndown chart data for a sprint"""
        total_tickets = sprint.tickets.count()
        total_estimated_hours = sprint.tickets.aggregate(
            total=Sum('estimated_hours')
        )['total'] or 0

        if total_tickets == 0:
            return {
                'ideal': [],
                'actual': [],
                'total_tickets': 0,
                'total_hours': 0,
                'remaining_tickets': 0,
                'remaining_hours': 0
            }

        duration_days = max((sprint.end_date - sprint.start_date).days, 1)

        ideal = []
        actual = []
        remaining_tickets = total_tickets
        remaining_hours = total_estimated_hours

        current_date = sprint.start_date.date()
        end_date = sprint.end_date.date()
        today = timezone.now().date()

        day_index = 0
        while current_date <= min(end_date, today):
            ideal_remaining = total_tickets - (total_tickets * day_index / duration_days)

            if current_date > sprint.start_date.date():
                completed_today = sprint.tickets.filter(
                    status=Ticket.Status.DONE,
                    completed_at__date=current_date
                ).count()
                hours_completed = sprint.tickets.filter(
                    status=Ticket.Status.DONE,
                    completed_at__date=current_date
                ).aggregate(total=Sum('estimated_hours'))['total'] or 0
                remaining_tickets -= completed_today
                remaining_hours -= hours_completed

            ideal.append({
                'date': current_date.isoformat(),
                'remaining': max(0, round(ideal_remaining, 1))
            })
            actual.append({
                'date': current_date.isoformat(),
                'remaining': max(0, remaining_tickets)
            })

            current_date += timedelta(days=1)
            day_index += 1

        return {
            'ideal': ideal,
            'actual': actual,
            'total_tickets': total_tickets,
            'total_hours': float(total_estimated_hours),
            'remaining_tickets': remaining_tickets,
            'remaining_hours': float(max(0, remaining_hours)),
        }

    @staticmethod
    def get_sprint_stats(sprint):
        """Get comprehensive sprint statistics"""
        tickets = sprint.tickets
        status_counts = tickets.values('status').annotate(count=Count('id'))
        by_status = {s['status']: s['count'] for s in status_counts}

        return {
            'total_tickets': tickets.count(),
            'backlog': by_status.get('backlog', 0),
            'todo': by_status.get('todo', 0),
            'in_progress': by_status.get('in_progress', 0),
            'review': by_status.get('review', 0),
            'done': by_status.get('done', 0),
            'progress': sprint.progress,
            'total_points': sprint.total_points,
            'completed_points': sprint.completed_points,
        }
