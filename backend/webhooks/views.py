from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from organizations.models import Organization
from .models import Webhook, WebhookLog
from .serializers import WebhookSerializer, WebhookCreateSerializer

class WebhookListCreateView(generics.ListCreateAPIView):
    """List and create webhooks for an organization"""
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WebhookCreateSerializer
        return WebhookSerializer

    def get_queryset(self):
        organization_id = self.kwargs['organization_id']
        return Webhook.objects.filter(
            organization_id=organization_id,
            is_active=True
        )

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization,
            id=self.kwargs['organization_id']
        )
        serializer.save(organization=organization)

class WebhookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a webhook"""
    
    queryset = Webhook.objects.filter(is_active=True)
    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]

class WebhookTestView(generics.GenericAPIView):
    """Test a webhook endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        webhook = get_object_or_404(Webhook, id=kwargs['pk'])
        
        test_payload = {
            'event': 'test',
            'data': {
                'message': 'Webhook test from TicketSaaS',
                'timestamp': timezone.now().isoformat()
            }
        }
        
        # Send test webhook
        import requests
        import json
        
        try:
            response = requests.post(
                webhook.url,
                json=test_payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-Signature': webhook.generate_signature(json.dumps(test_payload))
                },
                timeout=30
            )
            
            return Response({
                'status_code': response.status_code,
                'response': response.text[:500]  # Limit response size
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)