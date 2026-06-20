# organizations/urls.py
from django.urls import path
from .views import (
    OrganizationListCreateView, OrganizationDetailView,
    OrganizationMemberListView, OrganizationMemberAddView,
    OrganizationMemberUpdateView, OrganizationMemberRemoveView,
    InvitationCreateView, InvitationListView,
    InvitationAcceptView, InvitationDeclineView  # Add these imports
)

urlpatterns = [
    # Organization endpoints
    path('', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('<int:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    
    # Member endpoints
    path('<int:organization_id>/members/', OrganizationMemberListView.as_view(), name='member-list'),
    path('<int:organization_id>/members/add/', OrganizationMemberAddView.as_view(), name='member-add'),
    path('<int:organization_id>/members/update/', OrganizationMemberUpdateView.as_view(), name='member-update'),
    path('<int:organization_id>/members/remove/<int:user_id>/', OrganizationMemberRemoveView.as_view(), name='member-remove'),
    
    # Invitation endpoints
    path('<int:organization_id>/invitations/', InvitationListView.as_view(), name='invitation-list'),
    path('<int:organization_id>/invitations/create/', InvitationCreateView.as_view(), name='invitation-create'),
    
    # Public invitation endpoints (these are at the root level, not under organization)
    path('invitations/accept/', InvitationAcceptView.as_view(), name='invitation-accept'),
    path('invitations/decline/', InvitationDeclineView.as_view(), name='invitation-decline'),
]