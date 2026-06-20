Organizations App - Complete Documentation
📋 Overview
The Organizations App is a robust multi-tenant management system built with Django REST Framework. It enables users to create and manage organizations, invite members, assign roles, and control access permissions. This app serves as the foundation for team-based collaboration in the SaaS platform.

🎯 Purpose
The Organizations App provides:

Multi-tenant architecture - Each organization operates independently

Role-based access control (RBAC) - Fine-grained permissions for different user roles

Member management - Add, remove, and update member roles

Invitation system - Invite users to join organizations

Security - Soft deletion, last admin protection, and permission validation

🏗️ Architecture
Entity Relationship Diagram
text
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Organization  │         │   Membership    │         │      User       │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄────────│ organization_id │         │ id (PK)         │
│ name            │         │ user_id         │─────────│ username        │
│ slug            │         │ role            │         │ email           │
│ description     │         │ is_active       │         │ phone           │
│ website         │         │ joined_at       │         │ is_active       │
│ logo            │         │ updated_at      │         │ ...             │
│ created_by (FK) │─────────│ invited_by (FK) │─────────│                 │
│ created_at      │         └─────────────────┘         └─────────────────┘
│ updated_at      │                │
│ is_active       │                │
└─────────────────┘                │
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   Invitation    │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ email           │
                          │ organization_id │
                          │ role            │
                          │ invited_by (FK) │
                          │ token           │
                          │ status          │
                          │ expires_at      │
                          │ created_at      │
                          └─────────────────┘
📁 Module Structure
text
organizations/
├── __init__.py
├── admin.py           # Admin interface configuration
├── apps.py            # App configuration
├── models.py          # Database models (Organization, Membership, Invitation)
├── serializers.py     # Data serialization and validation
├── views.py           # API endpoints and business logic
├── urls.py            # URL routing
├── permissions.py     # Custom permission classes
├── tests.py           # Unit tests
└── utils.py           # Helper functions (optional)
📊 Data Models
1. Organization Model
The core entity representing a company or team.

python
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
Key Features:

Unique name and slug - Ensures organization identification

Soft delete - Organizations can be deactivated without data loss

Audit trail - Created/updated timestamps and creator tracking

Logo support - Image upload for organization branding

2. Membership Model
Represents the relationship between a user and an organization.

python
class Membership(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        DEVELOPER = 'developer', 'Developer'
        SUPPORT = 'support', 'Support'
        VIEWER = 'viewer', 'Viewer'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
Role Hierarchy:

text
ADMIN (Highest)
  └── MANAGER
        └── DEVELOPER
              └── SUPPORT
                    └── VIEWER (Lowest)
Role Permissions:

Permission	Admin	Manager	Developer	Support	Viewer
View Organization	✅	✅	✅	✅	✅
Edit Organization	✅	❌	❌	❌	❌
Delete Organization	✅	❌	❌	❌	❌
Add/Remove Members	✅	❌	❌	❌	❌
Update Member Roles	✅	❌	❌	❌	❌
Create Invitations	✅	✅	❌	❌	❌
View Invitations	✅	✅	❌	❌	❌
View Members	✅	✅	✅	✅	✅
Create Projects	✅	✅	✅	❌	❌
Create Tickets	✅	✅	✅	✅	❌
3. Invitation Model
Manages user invitations to join organizations.

python
class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        EXPIRED = 'expired', 'Expired'

    email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Membership.Role.choices)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
Invitation Flow:

text
1. Admin creates invitation
         │
2. User receives email with token
         │
3. User clicks accept/decline
         │
4. If accepted: User becomes member
         │
5. If expired: Invitation becomes invalid
🔐 Permissions System
Permission Classes
python
class IsOrganizationMember(permissions.BasePermission):
    """Check if user is a member of the organization."""
    
class IsOrganizationAdmin(permissions.BasePermission):
    """Check if user is an admin of the organization."""
    
class IsOrganizationManager(permissions.BasePermission):
    """Check if user is a manager or admin of the organization."""
Permission Matrix
Endpoint	Method	Permission Required
/organizations/	GET	Authenticated User
/organizations/	POST	Authenticated User
/organizations/{id}/	GET	Organization Member
/organizations/{id}/	PUT/PATCH	Organization Admin
/organizations/{id}/	DELETE	Organization Admin
/organizations/{id}/members/	GET	Organization Member
/organizations/{id}/members/add/	POST	Organization Admin
/organizations/{id}/members/update/	PUT	Organization Admin
/organizations/{id}/members/remove/	DELETE	Organization Admin
/organizations/{id}/invitations/	GET	Organization Manager
/organizations/{id}/invitations/create/	POST	Organization Admin
/invitations/accept/	POST	Any User
/invitations/decline/	POST	Any User
📡 API Endpoints
Complete API Reference
Method	Endpoint	Description	Auth
Organizations			
GET	/api/organizations/	List user's organizations	✅
POST	/api/organizations/	Create organization	✅
GET	/api/organizations/{id}/	Get organization details	✅
PUT	/api/organizations/{id}/	Update organization	✅
PATCH	/api/organizations/{id}/	Partial update	✅
DELETE	/api/organizations/{id}/	Delete (soft)	✅
Members			
GET	/api/organizations/{id}/members/	List members	✅
POST	/api/organizations/{id}/members/add/	Add member	✅
PUT	/api/organizations/{id}/members/update/	Update role	✅
DELETE	/api/organizations/{id}/members/remove/{user_id}/	Remove member	✅
Invitations			
GET	/api/organizations/{id}/invitations/	List invitations	✅
POST	/api/organizations/{id}/invitations/create/	Create invitation	✅
POST	/api/invitations/accept/	Accept invitation	❌
POST	/api/invitations/decline/	Decline invitation	❌
Example Request/Response
Create Organization
bash
POST /api/organizations/
Headers: Authorization: Bearer <token>
Request:

json
{
    "name": "Tech Corp",
    "description": "Leading technology company",
    "website": "https://techcorp.com"
}
Response:

json
{
    "id": 1,
    "name": "Tech Corp",
    "slug": "tech-corp",
    "description": "Leading technology company",
    "website": "https://techcorp.com",
    "logo": null,
    "created_by": 1,
    "created_by_email": "admin@org.com",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "is_active": true,
    "member_count": 1,
    "user_role": "admin",
    "is_admin": true
}
Add Member
bash
POST /api/organizations/1/members/add/
Headers: Authorization: Bearer <token>
Request:

json
{
    "user_id": 2,
    "role": "developer"
}
Response:

json
{
    "id": 1,
    "user": 2,
    "user_details": {
        "id": 2,
        "username": "devuser",
        "email": "dev@example.com",
        "phone": null,
        "avatar": null,
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z"
    },
    "organization": 1,
    "organization_details": {
        "id": 1,
        "name": "Tech Corp",
        "slug": "tech-corp",
        "description": "Leading technology company",
        "website": "https://techcorp.com",
        "logo": null,
        "created_by": 1,
        "created_by_email": "admin@org.com",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "is_active": true,
        "member_count": 2,
        "user_role": "admin",
        "is_admin": true
    },
    "role": "developer",
    "role_display": "Developer",
    "is_active": true,
    "joined_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
Create Invitation
bash
POST /api/organizations/1/invitations/create/
Headers: Authorization: Bearer <token>
Request:

json
{
    "email": "invited@example.com",
    "role": "viewer"
}
Response:

json
{
    "id": 1,
    "email": "invited@example.com",
    "organization": 1,
    "organization_name": "Tech Corp",
    "role": "viewer",
    "role_display": "Viewer",
    "invited_by": 1,
    "invited_by_email": "admin@org.com",
    "invited_by_username": "admin",
    "token": "abc123def456...",
    "status": "pending",
    "status_display": "Pending",
    "is_expired": false,
    "expires_at": "2024-01-08T12:00:00Z",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
🔧 Key Features
1. Soft Delete System
All deletions are soft to maintain data integrity:

Organizations: is_active = False

Memberships: is_active = False

Invitations: Status changed to EXPIRED

2. Last Admin Protection
Prevents accidental removal of the last administrator:

python
# Check before removing admin
if membership.role == Membership.Role.ADMIN:
    admin_count = Membership.objects.filter(
        organization_id=organization_id,
        role=Membership.Role.ADMIN,
        is_active=True
    ).count()
    if admin_count <= 1:
        return Response({
            "error": "Cannot remove the last admin of the organization"
        }, status=400)
3. Auto-Generated Slug
Slug is automatically generated from the organization name:

python
# Auto-generate slug
organization.slug = slugify(organization.name)
# Ensure uniqueness
base_slug = organization.slug
counter = 1
while Organization.objects.filter(slug=organization.slug).exists():
    organization.slug = f"{base_slug}-{counter}"
    counter += 1
4. Token-Based Invitations
Secure invitation tokens for joining organizations:

32-byte random tokens

7-day expiration

One-time use

🛡️ Security Considerations
1. Permission Checks
Every endpoint has strict permission checks:

API views use custom permission classes

All operations validate user's role

Database queries filter by active memberships

2. Data Isolation
Users can only access:

Organizations they belong to

Members of their organizations

Invitations to their organizations

3. Rate Limiting
Recommended rate limits:

python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
4. Input Validation
All serializers validate:

Required fields

Data types

Foreign key existence

Unique constraints

Role values

📈 Performance Optimization
1. Database Indexes
Recommended indexes:

python
class Meta:
    indexes = [
        models.Index(fields=['organization', 'user']),
        models.Index(fields=['user', 'is_active']),
        models.Index(fields=['organization', 'role']),
        models.Index(fields=['email', 'status']),
    ]
2. Query Optimization
Use select_related() for foreign keys

Use prefetch_related() for reverse relations

Filter queries early

python
members = Membership.objects.filter(
    organization_id=organization_id
).select_related('user', 'invited_by')
3. Caching
Cache frequently accessed data:

python
from django.core.cache import cache

def get_organization_stats(org_id):
    cache_key = f'org_stats_{org_id}'
    stats = cache.get(cache_key)
    if not stats:
        stats = calculate_stats(org_id)
        cache.set(cache_key, stats, 300)  # 5 minutes
    return stats
📝 Testing
Unit Tests Examples
python
# tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Organization, Membership

User = get_user_model()

class OrganizationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_organization(self):
        """Test creating an organization"""
        org = Organization.objects.create(
            name='Test Org',
            description='Test Description',
            created_by=self.user
        )
        self.assertEqual(org.name, 'Test Org')
        self.assertEqual(org.slug, 'test-org')
        self.assertTrue(org.is_active)
    
    def test_add_member(self):
        """Test adding a member to organization"""
        org = Organization.objects.create(
            name='Test Org',
            created_by=self.user
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        membership = Membership.objects.create(
            user=user2,
            organization=org,
            role=Membership.Role.DEVELOPER,
            invited_by=self.user
        )
        
        self.assertEqual(org.memberships.count(), 1)
        self.assertEqual(membership.role, Membership.Role.DEVELOPER)
API Tests
python
# test_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User

class OrganizationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_organization(self):
        """Test creating organization via API"""
        url = reverse('organization-list-create')
        data = {
            'name': 'Test Org',
            'description': 'Test Description',
            'website': 'https://test.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Org')
    
    def test_add_member(self):
        """Test adding member via API"""
        # Create organization
        org = Organization.objects.create(
            name='Test Org',
            created_by=self.user
        )
        
        # Create another user
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Add member
        url = reverse('member-add', kwargs={'organization_id': org.id})
        data = {'user_id': user2.id, 'role': 'developer'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
🚀 Deployment Checklist
Before Deployment
Set DEBUG = False in settings

Configure database connection

Set up media storage (S3, etc.)

Configure email backend for invitations

Set up CORS properly

Configure SSL/HTTPS

Set up logging

Run migrations

Create superuser

Test all endpoints

Set up monitoring

Environment Variables
bash
# .env
DEBUG=0
SECRET_KEY=<your-secret-key>
ALLOWED_HOSTS=yourdomain.com

# Database
DB_NAME=saas_db
DB_USER=saas_user
DB_PASSWORD=<secure-password>
DB_HOST=localhost

# Email (for invitations)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=notifications@yourdomain.com
EMAIL_HOST_PASSWORD=<email-password>

# Storage (for logos)
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
AWS_STORAGE_BUCKET_NAME=saas-media
AWS_S3_REGION_NAME=us-east-1
🔄 Integration with Other Apps
With Tickets App
python
# tickets/models.py
class Ticket(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # ... other fields
With Projects App
python
# projects/models.py
class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='ProjectMembership')
    # ... other fields
📚 Summary
The Organizations App provides:

✅ Multi-tenant support - Each organization is isolated
✅ Role-based access control - 5 different roles with specific permissions
✅ Member management - Add, update, remove members
✅ Invitation system - Secure email-based invitations
✅ Security features - Soft delete, last admin protection
✅ Production-ready - Optimized queries, caching ready
✅ Extensible - Easy to add new features
✅ Well-documented - Clear API documentation

This app serves as the foundation for team collaboration in the SaaS platform, ensuring proper access control and data isolation between different organizations.

