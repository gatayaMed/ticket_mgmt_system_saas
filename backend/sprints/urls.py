from django.urls import path
from .views import SprintListCreateView, SprintDetailView, SprintAddTicketsView, SprintCompleteView

urlpatterns = [
    path('projects/<int:project_id>/', SprintListCreateView.as_view(), name='sprint-list-create'),
    path('<int:pk>/', SprintDetailView.as_view(), name='sprint-detail'),
    path('<int:pk>/add-tickets/', SprintAddTicketsView.as_view(), name='sprint-add-tickets'),
    path('<int:pk>/complete/', SprintCompleteView.as_view(), name='sprint-complete'),
]
