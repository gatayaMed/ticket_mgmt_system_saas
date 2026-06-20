# tickets/urls.py
from django.urls import path
from .views import (
    TicketListCreateView, TicketDetailView,
    TicketStatusUpdateView, TicketAssignView,
    TicketHistoryView, TicketStatsView  # ADD THIS
)

app_name = 'tickets'

urlpatterns = [
    # Ticket endpoints
    path('projects/<int:project_id>/tickets/',
         TicketListCreateView.as_view(),
         name='ticket-list-create'),
    
    path('projects/<int:project_id>/tickets/stats/',
         TicketStatsView.as_view(),
         name='ticket-stats'),
    
    path('tickets/<int:pk>/',
         TicketDetailView.as_view(),
         name='ticket-detail'),
    
    path('tickets/<int:pk>/status/',
         TicketStatusUpdateView.as_view(),
         name='ticket-status-update'),
    
    path('tickets/<int:pk>/assign/',
         TicketAssignView.as_view(),
         name='ticket-assign'),
    
    path('tickets/<int:pk>/history/',
         TicketHistoryView.as_view(),
         name='ticket-history'),
]