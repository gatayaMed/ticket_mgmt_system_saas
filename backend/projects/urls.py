# projects/urls.py
from django.urls import path
from .views import (
    ProjectListCreateView, ProjectDetailView,
    ProjectMemberListView, ProjectMemberAddView,
    ProjectMemberUpdateView, ProjectMemberRemoveView
)

app_name = 'projects'

urlpatterns = [
    # Project endpoints
    path('organizations/<int:organization_id>/projects/',
         ProjectListCreateView.as_view(),
         name='project-list-create'),
    
    path('projects/<int:pk>/',
         ProjectDetailView.as_view(),
         name='project-detail'),
    
    # Project member endpoints
    path('projects/<int:project_id>/members/',
         ProjectMemberListView.as_view(),
         name='project-member-list'),
    
    path('projects/<int:project_id>/members/add/',
         ProjectMemberAddView.as_view(),
         name='project-member-add'),
    
    path('projects/<int:project_id>/members/update/',
         ProjectMemberUpdateView.as_view(),
         name='project-member-update'),
    
    path('projects/<int:project_id>/members/remove/<int:user_id>/',
         ProjectMemberRemoveView.as_view(),
         name='project-member-remove'),
]