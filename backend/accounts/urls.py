# accounts/urls.py
from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),          # api/auth/register/
    path('login/', LoginView.as_view(), name='login'),                  # api/auth/login/
    path('logout/', LogoutView.as_view(), name='logout'),               # api/auth/logout/
    path('profile/', ProfileView.as_view(), name='profile'),            # api/auth/profile/
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),  # api/auth/change-password/
]