from django.urls import path
from .views import WebhookListCreateView, WebhookDetailView, WebhookTestView

urlpatterns = [
    path('organizations/<int:organization_id>/', WebhookListCreateView.as_view(), name='webhook-list-create'),
    path('<int:pk>/', WebhookDetailView.as_view(), name='webhook-detail'),
    path('<int:pk>/test/', WebhookTestView.as_view(), name='webhook-test'),
]
