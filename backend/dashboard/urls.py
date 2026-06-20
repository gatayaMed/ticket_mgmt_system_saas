from django.urls import path
from .views import DashboardOverviewView, ProjectDashboardView

urlpatterns = [
    path('overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('projects/<int:project_id>/', ProjectDashboardView.as_view(), name='project-dashboard'),
]
