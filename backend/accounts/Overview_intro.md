Complete Authentication App Documentation
📋 Overview
This is a Django REST Framework (DRF) authentication system using JWT (JSON Web Tokens) via djangorestframework-simplejwt. It provides a complete user authentication flow including registration, login, logout, profile management, and password change functionality.

🏗️ Project Structure
text
accounts/
├── __init__.py
├── admin.py           # Django admin configuration
├── apps.py            # App configuration
├── models.py          # Custom User model
├── serializers.py     # Data validation & serialization
├── views.py           # API endpoints
├── urls.py            # URL routing
├── backends.py        # Custom authentication backends (optional)
└── permissions.py     # Custom permissions (optional)
📦 Dependencies
python
# requirements.txt
Django>=4.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.0
django-cors-headers>=3.0  # For CORS support
Pillow>=9.0              # For image handling (avatar)
1️⃣ Models (models.py)
Custom User Model
python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Extended User model with additional fields.
    Inherits from Django's AbstractUser which provides:
    - username, password, first_name, last_name
    - email, is_staff, is_active, is_superuser
    - date_joined, last_login
    - groups, user_permissions
    """
    
    # Custom Fields
    email = models.EmailField(unique=True)  # Email must be unique
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Override groups with custom related_name to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_user_groups',  # Prevents reverse accessor clashes
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_user_permissions',
        blank=True,
    )

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'  # Custom table name
        verbose_name = 'User'
        verbose_name_plural = 'Users'
Key Concepts:

AbstractUser: Provides all Django's built-in user functionality

related_name: Prevents conflicts between auth.User and accounts.User

db_table: Explicitly sets database table name

blank=True, null=True: Makes fields optional

2️⃣ Serializers (serializers.py)
Serializers handle data validation and conversion between Python objects and JSON.

UserSerializer
python
class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for displaying user data"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']  # These fields can't be edited
Purpose: Serialize User objects to JSON and vice versa.

RegisterSerializer
python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'phone']

    def validate(self, data):
        """Cross-field validation"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password2')  # Remove confirmation field
        user = User.objects.create_user(**validated_data)
        return user
Purpose: Handle user registration with password confirmation.

Key Features:

write_only=True: Password never returned in responses

min_length=8: Enforce password complexity

Password confirmation validation

Uses create_user() for proper password hashing

LoginSerializer
python
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # Can be username or email
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        # Try authenticating with username
        user = authenticate(username=username, password=password)
        
        # If failed and it looks like email, try with email
        if not user and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        
        return {'user': user}  # Return user in validated_data
Purpose: Authenticate users and validate credentials.

Key Features:

Supports login with username OR email

Checks if account is active

Returns user object for token generation

TokenSerializer
python
class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer(read_only=True)

    @classmethod
    def get_tokens_for_user(cls, user):
        """Helper method to generate JWT tokens"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }
Purpose: Structure JWT token responses.

JWT Token Details:

Access Token: Short-lived (default 5 minutes) - used for API authentication

Refresh Token: Long-lived (default 24 hours) - used to get new access tokens

3️⃣ Views (views.py)
Views handle HTTP requests and return HTTP responses.

RegisterView
python
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
Purpose: Create new user accounts.

Flow:

Validate registration data

Create user with hashed password

Generate JWT tokens

Return tokens and user data

Example Request:

json
POST /api/auth/register/
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password2": "securepass123",
    "phone": "+1234567890"
}
Example Response:

json
{
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z"
    }
}
LoginView
python
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can login

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }
        return Response(response_data)
Purpose: Authenticate existing users.

Flow:

Validate credentials

Get authenticated user

Generate JWT tokens

Return tokens and user data

Example Request:

json
POST /api/auth/login/
{
    "username": "john_doe",  // or email: "john@example.com"
    "password": "securepass123"
}
LogoutView
python
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]  # Must be logged in

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # Invalidate the token
            
            return Response(
                {"message": "Logged out successfully"}, 
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
Purpose: Invalidate refresh tokens to prevent reuse.

Important: Requires djangorestframework-simplejwt token blacklist feature.

Settings for Blacklist:

python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt.token_blacklist',
]

SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
Example Request:

python
POST /api/auth/logout/
Headers: Authorization: Bearer <access_token>
Body: {"refresh": "eyJhbGciOiJIUzI1NiIs..."}
ProfileView
python
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # Always return current user
Purpose: View and update user profile.

Key Features:

RetrieveUpdateAPIView: Provides GET and PUT/PATCH

get_object(): Always returns the authenticated user

Example Request (GET):

text
GET /api/auth/profile/
Headers: Authorization: Bearer <access_token>
Example Request (UPDATE):

json
PATCH /api/auth/profile/
Headers: Authorization: Bearer <access_token>
{
    "phone": "+9876543210",
    "email": "newemail@example.com"
}
4️⃣ URL Configuration (urls.py)
python
from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView
)

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
API Endpoints:

Method	Endpoint	Description	Auth Required
POST	/auth/register/	Create new account	❌
POST	/auth/login/	Login and get tokens	❌
POST	/auth/logout/	Invalidate refresh token	✅
GET/PATCH	/auth/profile/	View/Update profile	✅
POST	/auth/change-password/	Change password	✅
5️⃣ Authentication Flow
1. Registration Flow
text
User → RegisterView → Validate Data → Create User → Generate Tokens → Return Tokens
2. Login Flow
text
User → LoginView → Validate Credentials → Authenticate User → Generate Tokens → Return Tokens
3. API Request Flow (Authenticated)
text
Client → Send Request with Access Token → DRF Validates Token → Process Request → Return Response
4. Token Refresh Flow
text
Client → Refresh Token Expired → Send Refresh Token → Get New Access Token → Continue
6️⃣ JWT Token Structure
Access Token Payload (Decoded)
json
{
    "token_type": "access",
    "exp": 1704067200,  // Expiration timestamp
    "iat": 1704063600,  // Issued at timestamp
    "jti": "abc123",    // JWT ID
    "user_id": 1,
    "username": "john_doe"
}
Refresh Token Payload
json
{
    "token_type": "refresh",
    "exp": 1704150000,  // Longer expiration
    "iat": 1704063600,
    "jti": "xyz789",
    "user_id": 1
}
7️⃣ Security Best Practices
1. Password Security
Passwords are hashed using Django's PBKDF2

Minimum length enforced (8 characters)

Never return passwords in responses

2. Token Security
Access tokens: Short-lived (5-15 minutes)

Refresh tokens: Longer-lived (24 hours - 7 days)

Tokens stored client-side (localStorage or httpOnly cookies)

3. SSL/TLS
Always use HTTPS in production

Prevents token interception

4. CORS Configuration
python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://yourdomain.com",
]
5. Rate Limiting
python
# Add throttle classes to prevent brute force
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '100/minute'
    }
}
8️⃣ Django Settings Configuration
python
# settings.py

# Install apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    # Local apps
    'accounts',
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Authentication backends (if using email login)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # Add custom backend for email login if needed
]
9️⃣ Testing Guide
Test Registration
python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

def test_register_user():
    client = APIClient()
    response = client.post(reverse('accounts:register'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'password2': 'testpass123',
    })
    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.data
Test Login
python
def test_login_user():
    client = APIClient()
    # First create user
    response = client.post(reverse('accounts:register'), {...})
    # Then login
    response = client.post(reverse('accounts:login'), {
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 200
    assert 'access' in response.data
🔟 Common Use Cases
1. Making Authenticated API Calls
javascript
// Frontend (React)
const response = await fetch('/api/auth/profile/', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
});
2. Refreshing Access Token
javascript
const refreshToken = async () => {
    const response = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
    });
    const data = await response.json();
    return data.access;
};
3. Logout
javascript
const logout = async () => {
    await fetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh: refreshToken })
    });
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
};
🎯 Summary
This authentication system provides:

✅ Custom user model with extra fields

✅ JWT-based authentication

✅ Registration with email confirmation

✅ Login with username or email

✅ Logout with token blacklisting

✅ Profile viewing and updating

✅ Password change functionality

✅ Production-ready security features

✅ Scalable and maintainable architecture

The system follows Django and DRF best practices, making it secure, extensible, and easy to maintain.

