from django.urls import path
from .views import TicketReportView, ReportExportView

urlpatterns = [
    path('organizations/<int:organization_id>/tickets/', TicketReportView.as_view(), name='ticket-report'),
    path('export/', ReportExportView.as_view(), name='report-export'),
]
