# comments/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from tickets.models import Ticket
from projects.models import ProjectMember
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer

class CommentListCreateView(generics.ListCreateAPIView):
    """List all comments for a ticket and create new comments."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return Comment.objects.filter(
            ticket_id=ticket_id,
            is_active=True
        ).select_related('user')

    def perform_create(self, serializer):
        ticket = get_object_or_404(Ticket, id=self.kwargs['ticket_id'])
        
        # Check if user is a project member
        if not ProjectMember.objects.filter(
            project=ticket.project,
            user=self.request.user,
            is_active=True
        ).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You must be a project member to comment.")
        
        serializer.save(
            ticket=ticket,
            user=self.request.user
        )

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a comment."""
    
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        comment = self.get_object()
        
        # Only allow the comment author to update
        if comment.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own comments.")
        
        serializer.save(is_edited=True)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()