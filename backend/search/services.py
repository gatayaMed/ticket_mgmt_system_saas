from django.db.models import Q
from tickets.models import Ticket
from projects.models import Project
from organizations.models import Organization
from accounts.models import User


class SearchService:
    @staticmethod
    def global_search(query, user):
        """Search across all entities"""
        results = {
            'tickets': [],
            'projects': [],
            'organizations': [],
            'users': [],
        }

        if not query or len(query) < 2:
            return results

        org_ids = Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).values_list('id', flat=True)

        # Search tickets
        results['tickets'] = Ticket.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ticket_id__icontains=query),
            Q(project__organization_id__in=org_ids) |
            Q(assignee=user) |
            Q(created_by=user),
            is_active=True
        ).select_related('project', 'assignee')[:20]

        # Search projects
        results['projects'] = Project.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            organization_id__in=org_ids,
            is_active=True
        )[:10]

        # Search organizations
        results['organizations'] = Organization.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            id__in=org_ids,
            is_active=True
        ).distinct()[:5]

        # Search users in organizations
        results['users'] = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            memberships__organization_id__in=org_ids,
            memberships__is_active=True,
        ).distinct()[:10]

        return results

    @staticmethod
    def advanced_ticket_search(filters, user):
        """Advanced search for tickets with multiple filters"""
        org_ids = Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).values_list('id', flat=True)

        tickets = Ticket.objects.filter(
            project__organization_id__in=org_ids,
            is_active=True
        )

        # Apply filters
        if filters.get('status'):
            tickets = tickets.filter(status=filters['status'])
        if filters.get('priority'):
            tickets = tickets.filter(priority=filters['priority'])
        if filters.get('ticket_type'):
            tickets = tickets.filter(ticket_type=filters['ticket_type'])
        if filters.get('assignee'):
            tickets = tickets.filter(assignee_id=filters['assignee'])
        if filters.get('project'):
            tickets = tickets.filter(project_id=filters['project'])
        if filters.get('created_by'):
            tickets = tickets.filter(created_by_id=filters['created_by'])
        if filters.get('from_date'):
            tickets = tickets.filter(created_at__gte=filters['from_date'])
        if filters.get('to_date'):
            tickets = tickets.filter(created_at__lte=filters['to_date'])
        if filters.get('search'):
            query = filters['search']
            tickets = tickets.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(ticket_id__icontains=query)
            )

        return tickets
