# attachments/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from tickets.models import Ticket
from projects.models import ProjectMember
from .models import Attachment
from .serializers import AttachmentSerializer, AttachmentCreateSerializer

class AttachmentListCreateView(generics.ListCreateAPIView):
    """List all attachments for a ticket and upload new attachments."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttachmentCreateSerializer
        return AttachmentSerializer

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return Attachment.objects.filter(
            ticket_id=ticket_id,
            is_active=True
        ).order_by('-created_at')

    def perform_create(self, serializer):
        ticket = get_object_or_404(Ticket, id=self.kwargs['ticket_id'])
        
        # Check if user is a project member
        if not ProjectMember.objects.filter(
            project=ticket.project,
            user=self.request.user,
            is_active=True
        ).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a project member to upload attachments.")
        
        serializer.save(
            ticket=ticket,
            user=self.request.user
        )

class AttachmentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete an attachment."""
    
    queryset = Attachment.objects.filter(is_active=True)
    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Download the attachment file."""
        instance = self.get_object()
        
        # Check if user has access to the ticket
        if not ProjectMember.objects.filter(
            project=instance.ticket.project,
            user=request.user,
            is_active=True
        ).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have access to this attachment.")
        
        # Return the file
        response = FileResponse(instance.file, content_type=instance.content_type)
        response['Content-Disposition'] = f'attachment; filename="{instance.filename}"'
        return response

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()