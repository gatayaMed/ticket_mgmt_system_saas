from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .services import SearchService
from .serializers import (
    TicketSearchResultSerializer, ProjectSearchResultSerializer,
    OrganizationSearchResultSerializer, GlobalSearchResponseSerializer,
    AdvancedTicketSearchSerializer
)
from accounts.serializers import UserSerializer


class GlobalSearchView(generics.GenericAPIView):
    """Search across all entities (tickets, projects, organizations, users)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response(
                {'error': 'Search query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = SearchService.global_search(query, request.user)

        response_data = {
            'tickets': TicketSearchResultSerializer(results['tickets'], many=True).data,
            'projects': ProjectSearchResultSerializer(results['projects'], many=True).data,
            'organizations': OrganizationSearchResultSerializer(results['organizations'], many=True).data,
            'users': UserSerializer(results['users'], many=True).data,
        }

        return Response(response_data)


class AdvancedTicketSearchView(generics.GenericAPIView):
    """Advanced ticket search with multiple filters"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filters = {
            'status': request.query_params.get('status'),
            'priority': request.query_params.get('priority'),
            'ticket_type': request.query_params.get('ticket_type'),
            'assignee': request.query_params.get('assignee'),
            'project': request.query_params.get('project'),
            'search': request.query_params.get('search'),
            'due_date_from': request.query_params.get('due_date_from'),
            'due_date_to': request.query_params.get('due_date_to'),
        }
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}

        tickets = SearchService.advanced_ticket_search(filters, request.user)
        serializer = TicketSearchResultSerializer(tickets, many=True)

        return Response({
            'count': tickets.count(),
            'results': serializer.data
        })
