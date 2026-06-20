# dashboard/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from projects.models import Project
from .services import DashboardService

class DashboardOverviewView(generics.GenericAPIView):
    """Get dashboard overview statistics"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stats = DashboardService.get_overview_stats(request.user)
        return Response(stats)

class ProjectDashboardView(generics.GenericAPIView):
    """Get project-specific dashboard statistics"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project_id = kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        stats = DashboardService.get_project_stats(project_id)
        return Response(stats)