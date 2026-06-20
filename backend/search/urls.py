from django.urls import path
from .views import GlobalSearchView, AdvancedTicketSearchView

urlpatterns = [
    path('', GlobalSearchView.as_view(), name='global-search'),
    path('tickets/advanced/', AdvancedTicketSearchView.as_view(), name='advanced-ticket-search'),
]
