from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Ticket, TicketHistory
from .serializers import (
    TicketSerializer, TicketCreateSerializer,
    TicketUpdateSerializer, TicketHistorySerializer
)
from projects.models import Project, ProjectMember

User = get_user_model() 

# tickets/views.py
class TicketListCreateView(generics.ListCreateAPIView):
    """List tickets for a project and create new tickets."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TicketCreateSerializer
        return TicketSerializer

    def get_serializer_context(self):
        # Add project and organization to serializer context
        context = super().get_serializer_context()
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        context['project'] = project
        context['organization'] = project.organization
        return context

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        queryset = Ticket.objects.filter(
            project_id=project_id,
            is_active=True
        ).select_related('assignee', 'created_by', 'project', 'organization')
        
        # Apply filters...
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        ticket_type = self.request.query_params.get('ticket_type')
        assignee = self.request.query_params.get('assignee')
        search = self.request.query_params.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if ticket_type:
            queryset = queryset.filter(ticket_type=ticket_type)
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(ticket_id__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        organization = project.organization
        
        # Check if user is project member
        if not ProjectMember.objects.filter(
            project=project,
            user=self.request.user,
            is_active=True
        ).exists():
            raise PermissionDenied("You must be a project member to create tickets.")
        
        ticket = serializer.save(
            project=project,
            organization=organization,
            created_by=self.request.user
        )
        
        # Create history entry
        TicketHistory.objects.create(
            ticket=ticket,
            user=self.request.user,
            action=TicketHistory.Action.CREATED,
            description=f"Created ticket {ticket.ticket_id}"
        )

class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a ticket."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TicketUpdateSerializer
        return TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(is_active=True)

    def check_permissions(self, request):
        super().check_permissions(request)
        ticket = self.get_object()
        
        # Only assignee, creator, or project lead can update
        if request.method in ['PUT', 'PATCH']:
            is_creator = ticket.created_by == request.user
            is_assignee = ticket.assignee == request.user
            is_project_lead = ProjectMember.objects.filter(
                project=ticket.project,
                user=request.user,
                role=ProjectMember.Role.PROJECT_LEAD,
                is_active=True
            ).exists()
            
            if not (is_creator or is_assignee or is_project_lead):
                raise PermissionDenied(
                    "You don't have permission to update this ticket."
                )

    def perform_update(self, serializer):
        ticket = self.get_object()
        old_status = ticket.status
        old_priority = ticket.priority
        old_assignee = ticket.assignee
        
        updated_ticket = serializer.save()
        
        # Track status changes
        if old_status != updated_ticket.status:
            TicketHistory.objects.create(
                ticket=updated_ticket,
                user=self.request.user,
                action=TicketHistory.Action.STATUS_CHANGED,
                old_value={'status': old_status},
                new_value={'status': updated_ticket.status},
                description=f"Status changed from {old_status} to {updated_ticket.status}"
            )
        
        # Track priority changes
        if old_priority != updated_ticket.priority:
            TicketHistory.objects.create(
                ticket=updated_ticket,
                user=self.request.user,
                action=TicketHistory.Action.PRIORITY_CHANGED,
                old_value={'priority': old_priority},
                new_value={'priority': updated_ticket.priority},
                description=f"Priority changed from {old_priority} to {updated_ticket.priority}"
            )
        
        # Track assignment changes
        if old_assignee != updated_ticket.assignee:
            TicketHistory.objects.create(
                ticket=updated_ticket,
                user=self.request.user,
                action=TicketHistory.Action.ASSIGNED,
                old_value={'assignee': old_assignee.id if old_assignee else None},
                new_value={'assignee': updated_ticket.assignee.id if updated_ticket.assignee else None},
                description=f"Ticket assigned to {updated_ticket.assignee.email if updated_ticket.assignee else 'Unassigned'}"
            )

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()
        
        TicketHistory.objects.create(
            ticket=instance,
            user=self.request.user,
            action=TicketHistory.Action.UPDATED,
            description=f"Ticket {instance.ticket_id} was archived"
        )



class TicketHistoryView(generics.ListAPIView):
    """Get history of a ticket."""
    
    serializer_class = TicketHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ticket = get_object_or_404(Ticket, id=self.kwargs['pk'])
        return TicketHistory.objects.filter(ticket=ticket)

class TicketStatusUpdateView(generics.GenericAPIView):
    """Update only the status of a ticket."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id=kwargs['pk'], is_active=True)
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {"error": "status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Ticket.Status.choices):
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = ticket.status
        ticket.status = new_status
        
        if new_status == Ticket.Status.DONE:
            ticket.completed_at = timezone.now()
        elif new_status != Ticket.Status.DONE:
            ticket.completed_at = None
        
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action=TicketHistory.Action.STATUS_CHANGED,
            old_value={'status': old_status},
            new_value={'status': new_status},
            description=f"Status changed from {old_status} to {new_status}"
        )
        
        return Response(TicketSerializer(ticket).data)

class TicketAssignView(generics.GenericAPIView):
    """Assign or unassign a ticket."""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, id=kwargs['pk'], is_active=True)
        assignee_id = request.data.get('assignee_id')
        
        old_assignee = ticket.assignee
        
        if assignee_id:
            
            User = get_user_model()
            
            # Check if assignee is a project member
            if not ProjectMember.objects.filter(
                project=ticket.project,
                user_id=assignee_id,
                is_active=True
            ).exists():
                return Response(
                    {"error": "Assignee must be a project member."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assignee = get_object_or_404(User, id=assignee_id)
            ticket.assignee = assignee
        else:
            ticket.assignee = None
        
        ticket.save()
        
        TicketHistory.objects.create(
            ticket=ticket,
            user=request.user,
            action=TicketHistory.Action.ASSIGNED,
            old_value={'assignee': old_assignee.id if old_assignee else None},
            new_value={'assignee': ticket.assignee.id if ticket.assignee else None},
            description=f"Ticket assigned to {ticket.assignee.email if ticket.assignee else 'Unassigned'}"
        )
        
        return Response(TicketSerializer(ticket).data)



# tickets/views.py
class TicketStatsView(generics.GenericAPIView):
    """Get ticket statistics for a project."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        
        # Get all tickets for the project
        tickets = Ticket.objects.filter(
            project_id=project_id,
            is_active=True
        )
        
        stats = {
            'total': tickets.count(),
            'by_status': {},
            'by_priority': {},
            'by_type': {},
            'assigned_to_me': tickets.filter(assignee=request.user).count(),
            'created_by_me': tickets.filter(created_by=request.user).count(),
            'overdue': tickets.filter(
                due_date__lt=timezone.now(),
                status__in=[Ticket.Status.TODO, Ticket.Status.IN_PROGRESS, Ticket.Status.REVIEW]
            ).count(),
            'completed_this_week': tickets.filter(
                completed_at__gte=timezone.now() - timezone.timedelta(days=7),
                status=Ticket.Status.DONE
            ).count(),
        }
        
        # Count by status
        for status in Ticket.Status.choices:
            stats['by_status'][status[0]] = tickets.filter(status=status[0]).count()
        
        # Count by priority
        for priority in Ticket.Priority.choices:
            stats['by_priority'][priority[0]] = tickets.filter(priority=priority[0]).count()
        
        # Count by type
        for ticket_type in Ticket.Type.choices:
            stats['by_type'][ticket_type[0]] = tickets.filter(ticket_type=ticket_type[0]).count()
        
        return Response(stats)