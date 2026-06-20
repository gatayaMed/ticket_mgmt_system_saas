# sprints/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from projects.models import Project
from .models import Sprint, SprintHistory
from .serializers import SprintSerializer, SprintCreateSerializer

class SprintListCreateView(generics.ListCreateAPIView):
    """List and create sprints for a project"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SprintCreateSerializer
        return SprintSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Sprint.objects.filter(
            project_id=project_id,
            is_active=True
        ).prefetch_related('tickets')

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        serializer.save(
            project=project,
            created_by=self.request.user
        )

class SprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a sprint"""
    
    queryset = Sprint.objects.filter(is_active=True)
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class SprintAddTicketsView(generics.GenericAPIView):
    """Add tickets to a sprint"""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sprint = get_object_or_404(Sprint, id=kwargs['pk'])
        ticket_ids = request.data.get('ticket_ids', [])
        
        if not ticket_ids:
            return Response(
                {"error": "ticket_ids is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate tickets belong to the project
        from tickets.models import Ticket
        tickets = Ticket.objects.filter(
            id__in=ticket_ids,
            project=sprint.project,
            is_active=True
        )
        
        sprint.tickets.add(*tickets)
        
        # Create history entry
        SprintHistory.objects.create(
            sprint=sprint,
            user=request.user,
            action='tickets_added',
            description=f"Added {tickets.count()} tickets to sprint"
        )
        
        return Response(SprintSerializer(sprint).data)

class SprintCompleteView(generics.GenericAPIView):
    """Complete a sprint"""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sprint = get_object_or_404(Sprint, id=kwargs['pk'])
        
        if sprint.status == Sprint.Status.COMPLETED:
            return Response(
                {"error": "Sprint is already completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sprint.status = Sprint.Status.COMPLETED
        sprint.completed_at = timezone.now()
        sprint.save()
        
        SprintHistory.objects.create(
            sprint=sprint,
            user=request.user,
            action='completed',
            description=f"Sprint {sprint.name} completed"
        )
        
        return Response(SprintSerializer(sprint).data)