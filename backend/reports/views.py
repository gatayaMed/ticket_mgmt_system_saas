# reports/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from organizations.models import Organization
from .services import ReportService

class TicketReportView(generics.GenericAPIView):
    """Generate ticket reports"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        organization_id = kwargs['organization_id']
        organization = get_object_or_404(Organization, id=organization_id)
        
        # Check if user is a member
        if not organization.memberships.filter(
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {"error": "You don't have access to this organization"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        report = ReportService.generate_ticket_report(
            organization_id,
            start_date,
            end_date
        )
        
        return Response(report)

class ReportExportView(generics.GenericAPIView):
    """Export reports in CSV or JSON format"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        format = request.query_params.get('format', 'json')
        data = request.query_params.get('data', '[]')
        
        try:
            data = json.loads(data)
        except:
            return Response(
                {"error": "Invalid data format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if format == 'csv':
            return ReportService.export_csv(data)
        else:
            return ReportService.export_json(data)