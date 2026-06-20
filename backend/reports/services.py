import csv
import json
from io import StringIO
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Count, Q, Sum, Avg
from tickets.models import Ticket
from projects.models import Project
from organizations.models import Organization

class ReportService:
    @staticmethod
    def generate_ticket_report(organization_id, start_date=None, end_date=None):
        """Generate ticket report for an organization"""
        tickets = Ticket.objects.filter(
            organization_id=organization_id,
            is_active=True
        )
        
        if start_date:
            tickets = tickets.filter(created_at__gte=start_date)
        if end_date:
            tickets = tickets.filter(created_at__lte=end_date)
        
        # Summary statistics
        summary = {
            'total': tickets.count(),
            'by_status': tickets.values('status').annotate(count=Count('id')),
            'by_priority': tickets.values('priority').annotate(count=Count('id')),
            'by_type': tickets.values('ticket_type').annotate(count=Count('id')),
            'by_project': tickets.values('project__name').annotate(count=Count('id')),
            'by_assignee': tickets.values('assignee__username').annotate(count=Count('id')),
            'avg_completion_time': ReportService._calculate_avg_completion_time(tickets),
            'recent_activity': ReportService._get_recent_activity(tickets),
        }
        
        return summary

    @staticmethod
    def export_csv(data, filename='report.csv'):
        """Export data to CSV"""
        output = StringIO()
        if not data:
            return HttpResponse("No data to export", content_type='text/plain')
        
        # Get headers from first item
        headers = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def export_json(data, filename='report.json'):
        """Export data to JSON"""
        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type='application/json'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @staticmethod
    def _calculate_avg_completion_time(tickets):
        completed = tickets.filter(
            status=Ticket.Status.DONE,
            completed_at__isnull=False
        )
        if not completed.exists():
            return None
        
        total_days = sum(
            (t.completed_at - t.created_at).days
            for t in completed
        )
        return total_days / completed.count()

    @staticmethod
    def _get_recent_activity(tickets, limit=10):
        return tickets.order_by('-updated_at')[:limit].values(
            'id', 'ticket_id', 'title', 'status', 'updated_at'
        )