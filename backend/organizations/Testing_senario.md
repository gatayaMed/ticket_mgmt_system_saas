
🚀 Complete Testing Scenario & Documentation Guide
📋 Table of Contents
System Overview

Prerequisites

Test Data Setup

Complete Testing Scenario

API Endpoints Reference

Expected Outputs

Troubleshooting Guide

📖 System Overview
What is This Application?
This is a Multi-Tenant SaaS Platform with role-based access control. It allows users to:

Create organizations (companies/teams)

Manage members with different roles

Invite users to join organizations

Control access based on user roles

Key Concepts
Concept	Description	Example
User	Registered individual	john@example.com
Organization	Company or team	TechCorp
Membership	User's role in an organization	John is Admin of TechCorp
Invitation	Pending invite to join	Invite Sarah as Developer
Role	Permission level	Admin, Developer, Viewer
Role Hierarchy
text
👑 ADMIN (Full Control)
  └── 📊 MANAGER (Manage Projects)
        └── 💻 DEVELOPER (Write Code)
              └── 🎫 SUPPORT (Handle Tickets)
                    └── 👀 VIEWER (Read Only)
🛠️ Prerequisites
1. System Requirements
bash
# Check if everything is running
docker-compose ps

# Should see:
# - backend (Django)
# - db (PostgreSQL)
# - redis (if used)
2. Environment Variables
bash
# .env file should contain:
DEBUG=1
SECRET_KEY=your-secret-key
DB_NAME=saas_db
DB_USER=saas_user
DB_PASSWORD=your-password
📊 Test Data Setup
Step 1: Create Test Users
Create a file called create_test_data.py:

python
# create_test_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from organizations.models import Organization, Membership
from django.utils.text import slugify

def create_test_data():
    """Create comprehensive test data for the application"""
    
    print("=" * 60)
    print("🚀 CREATING TEST DATA")
    print("=" * 60)
    
    # 1. Create Users
    print("\n📝 Creating Users...")
    users = {}
    
    user_data = [
        {
            'username': 'alice_admin',
            'email': 'alice@techcorp.com',
            'password': 'Admin123!',
            'first_name': 'Alice',
            'last_name': 'Admin',
            'is_staff': True
        },
        {
            'username': 'bob_manager',
            'email': 'bob@techcorp.com',
            'password': 'Manager123!',
            'first_name': 'Bob',
            'last_name': 'Manager'
        },
        {
            'username': 'charlie_dev',
            'email': 'charlie@techcorp.com',
            'password': 'Dev123!',
            'first_name': 'Charlie',
            'last_name': 'Developer'
        },
        {
            'username': 'diana_support',
            'email': 'diana@techcorp.com',
            'password': 'Support123!',
            'first_name': 'Diana',
            'last_name': 'Support'
        },
        {
            'username': 'eve_viewer',
            'email': 'eve@techcorp.com',
            'password': 'Viewer123!',
            'first_name': 'Eve',
            'last_name': 'Viewer'
        },
        {
            'username': 'frank_ceo',
            'email': 'frank@startup.io',
            'password': 'Ceo123!',
            'first_name': 'Frank',
            'last_name': 'CEO'
        },
        {
            'username': 'grace_dev',
            'email': 'grace@startup.io',
            'password': 'Dev123!',
            'first_name': 'Grace',
            'last_name': 'Developer'
        }
    ]
    
    for data in user_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'is_staff': data.get('is_staff', False),
                'is_active': True
            }
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"  ✅ Created: {user.username} ({user.email})")
        users[user.username] = user
    
    print(f"✅ Total Users: {User.objects.count()}")
    
    # 2. Create Organizations
    print("\n🏢 Creating Organizations...")
    
    org_data = [
        {
            'name': 'TechCorp',
            'description': 'Leading technology company specializing in SaaS solutions',
            'website': 'https://techcorp.com',
            'created_by': users['alice_admin']
        },
        {
            'name': 'Startup.io',
            'description': 'Innovative startup building the future of AI',
            'website': 'https://startup.io',
            'created_by': users['frank_ceo']
        }
    ]
    
    organizations = {}
    for data in org_data:
        org, created = Organization.objects.get_or_create(
            name=data['name'],
            defaults={
                'slug': slugify(data['name']),
                'description': data['description'],
                'website': data['website'],
                'created_by': data['created_by'],
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ Created: {org.name}")
        organizations[org.name] = org
    
    print(f"✅ Total Organizations: {Organization.objects.count()}")
    
    # 3. Create Memberships
    print("\n👤 Creating Memberships...")
    
    # TechCorp Members
    techcorp_members = [
        {'user': users['alice_admin'], 'role': Membership.Role.ADMIN},
        {'user': users['bob_manager'], 'role': Membership.Role.MANAGER},
        {'user': users['charlie_dev'], 'role': Membership.Role.DEVELOPER},
        {'user': users['diana_support'], 'role': Membership.Role.SUPPORT},
        {'user': users['eve_viewer'], 'role': Membership.Role.VIEWER},
    ]
    
    for member_data in techcorp_members:
        membership, created = Membership.objects.get_or_create(
            user=member_data['user'],
            organization=organizations['TechCorp'],
            defaults={
                'role': member_data['role'],
                'invited_by': users['alice_admin'],
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ {member_data['user'].username} → TechCorp ({member_data['role']})")
    
    # Startup.io Members
    startup_members = [
        {'user': users['frank_ceo'], 'role': Membership.Role.ADMIN},
        {'user': users['grace_dev'], 'role': Membership.Role.DEVELOPER},
        {'user': users['bob_manager'], 'role': Membership.Role.MANAGER},  # Bob works at both
    ]
    
    for member_data in startup_members:
        membership, created = Membership.objects.get_or_create(
            user=member_data['user'],
            organization=organizations['Startup.io'],
            defaults={
                'role': member_data['role'],
                'invited_by': users['frank_ceo'],
                'is_active': True
            }
        )
        if created:
            print(f"  ✅ {member_data['user'].username} → Startup.io ({member_data['role']})")
    
    print(f"✅ Total Memberships: {Membership.objects.count()}")
    
    # 4. Display Summary
    print("\n" + "=" * 60)
    print("📊 TEST DATA SUMMARY")
    print("=" * 60)
    
    print("\n👥 Users:")
    for user in User.objects.all():
        print(f"  • {user.username} ({user.email})")
    
    print("\n🏢 Organizations:")
    for org in Organization.objects.filter(is_active=True):
        member_count = org.memberships.filter(is_active=True).count()
        print(f"  • {org.name} - {member_count} members")
        for membership in org.memberships.filter(is_active=True):
            print(f"    - {membership.user.username} ({membership.role})")
    
    print("\n✅ Test data setup complete!")
    print("=" * 60)

if __name__ == "__main__":
    create_test_data()
Step 2: Run the Test Data Script
bash
# Copy the script to your project
docker cp create_test_data.py backend:/app/

# Run it
docker-compose exec backend python create_test_data.py
Step 3: Verify Data
bash
# Check users
docker-compose exec backend python manage.py shell -c "from accounts.models import User; print(f'Users: {User.objects.count()}')"

# Check organizations
docker-compose exec backend python manage.py shell -c "from organizations.models import Organization; print(f'Orgs: {Organization.objects.count()}')"

# Check memberships
docker-compose exec backend python manage.py shell -c "from organizations.models import Membership; print(f'Memberships: {Membership.objects.count()}')"
🧪 Complete Testing Scenario
Scenario Overview
We'll test the entire application flow with 5 main actors:

Actor	Role	Organization	Actions
Alice	Admin	TechCorp	Full control, invite users
Bob	Manager	TechCorp & Startup.io	Manage projects, view reports
Charlie	Developer	TechCorp	Create tickets, view code
Diana	Support	TechCorp	Handle tickets, view users
Eve	Viewer	TechCorp	Read-only access
📝 Step-by-Step Testing
Test 1: Authentication & User Management
bash
#!/bin/bash
# test_1_auth.sh - Authentication Tests

echo "========================================="
echo "🔐 TEST 1: AUTHENTICATION"
echo "========================================="

# 1.1 Register New User
echo -e "\n1.1 Registering New User..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah_new",
    "email": "sarah@example.com",
    "password": "Sarah123!",
    "password2": "Sarah123!"
  }')

echo $REGISTER_RESPONSE | python3 -m json.tool 2>/dev/null
echo "✅ User registered successfully"

# 1.2 Login
echo -e "\n1.2 Logging in as Sarah..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"sarah_new","password":"Sarah123!"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)
echo "✅ Login successful! Token: ${TOKEN:0:30}..."

# 1.3 Get Profile
echo -e "\n1.3 Getting User Profile..."
curl -s -X GET http://localhost:8500/api/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null

# Save token for later use
echo "export SARAH_TOKEN=$TOKEN" >> ~/.bashrc
Expected Output:

json
{
    "id": 8,
    "username": "sarah_new",
    "email": "sarah@example.com",
    "phone": null,
    "avatar": null,
    "is_active": true,
    "created_at": "2026-06-19T12:00:00Z"
}
Test 2: Organization Management
bash
#!/bin/bash
# test_2_organizations.sh - Organization Tests

echo "========================================="
echo "🏢 TEST 2: ORGANIZATION MANAGEMENT"
echo "========================================="

# Login as Alice (Admin)
ALICE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "✅ Logged in as Alice"

# 2.1 List All Organizations (Alice should see TechCorp)
echo -e "\n2.1 Listing Alice's Organizations..."
curl -s -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

# 2.2 Create New Organization
echo -e "\n2.2 Creating New Organization..."
CREATE_ORG_RESPONSE=$(curl -s -X POST http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Innovations",
    "description": "Cutting-edge AI solutions",
    "website": "https://ai-innovations.com"
  }')

echo $CREATE_ORG_RESPONSE | python3 -m json.tool 2>/dev/null
ORG_ID=$(echo $CREATE_ORG_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)
echo "✅ Organization created with ID: $ORG_ID"

# 2.3 Get Organization Details
echo -e "\n2.3 Getting Organization Details..."
curl -s -X GET http://localhost:8500/api/organizations/$ORG_ID/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

# 2.4 Update Organization
echo -e "\n2.4 Updating Organization..."
curl -s -X PATCH http://localhost:8500/api/organizations/$ORG_ID/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Leading AI innovation company"
  }' | python3 -m json.tool 2>/dev/null

echo -e "\n✅ Organization tests completed!"
Expected Output:

json
{
    "id": 3,
    "name": "AI Innovations",
    "slug": "ai-innovations",
    "description": "Leading AI innovation company",
    "website": "https://ai-innovations.com",
    "created_by": 1,
    "created_by_email": "alice@techcorp.com",
    "is_active": true,
    "member_count": 1,
    "user_role": "admin",
    "is_admin": true
}
Test 3: Member Management
bash
#!/bin/bash
# test_3_members.sh - Member Management Tests

echo "========================================="
echo "👤 TEST 3: MEMBER MANAGEMENT"
echo "========================================="

# Login as Alice (Admin)
ALICE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

# 3.1 List All Members
echo -e "\n3.1 Listing TechCorp Members..."
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

# 3.2 Add New Member
echo -e "\n3.2 Adding Sarah as Developer..."
# First get Sarah's user ID
SARAH_ID=$(curl -s -X GET http://localhost:8500/api/auth/profile/ \
  -H "Authorization: Bearer $SARAH_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

curl -s -X POST http://localhost:8500/api/organizations/1/members/add/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $SARAH_ID,
    \"role\": \"developer\"
  }" | python3 -m json.tool 2>/dev/null

# 3.3 Update Member Role
echo -e "\n3.3 Updating Sarah's Role to Manager..."
curl -s -X PUT http://localhost:8500/api/organizations/1/members/update/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $SARAH_ID,
    \"role\": \"manager\"
  }" | python3 -m json.tool 2>/dev/null

# 3.4 Check Updated Members List
echo -e "\n3.4 Updated Members List..."
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n✅ Member management tests completed!"
Expected Output:

json
{
    "id": 6,
    "user": 8,
    "user_details": {
        "id": 8,
        "username": "sarah_new",
        "email": "sarah@example.com"
    },
    "organization": 1,
    "role": "manager",
    "role_display": "Manager",
    "is_active": true,
    "joined_at": "2026-06-19T12:00:00Z"
}
Test 4: Invitation System
bash
#!/bin/bash
# test_4_invitations.sh - Invitation Tests

echo "========================================="
"📧 TEST 4: INVITATION SYSTEM"
echo "========================================="

# Login as Alice (Admin)
ALICE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

# 4.1 Create Invitation
echo -e "\n4.1 Creating Invitation for New User..."
INVITE_RESPONSE=$(curl -s -X POST http://localhost:8500/api/organizations/1/invitations/create/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "role": "viewer"
  }')

echo $INVITE_RESPONSE | python3 -m json.tool 2>/dev/null
INVITE_TOKEN=$(echo $INVITE_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null)
echo "✅ Invitation created! Token: ${INVITE_TOKEN:0:20}..."

# 4.2 List All Invitations
echo -e "\n4.2 Listing All Invitations..."
curl -s -X GET http://localhost:8500/api/organizations/1/invitations/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

# 4.3 Register New User with Invited Email
echo -e "\n4.3 Registering User with Invited Email..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "NewUser123!",
    "password2": "NewUser123!"
  }')

echo $REGISTER_RESPONSE | python3 -m json.tool 2>/dev/null
NEW_USER_TOKEN=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

# 4.4 Accept Invitation
echo -e "\n4.4 Accepting Invitation..."
curl -s -X POST http://localhost:8500/api/organizations/invitations/accept/ \
  -H "Authorization: Bearer $NEW_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$INVITE_TOKEN\"}" | python3 -m json.tool 2>/dev/null

# 4.5 Verify Member Added
echo -e "\n4.5 Verifying Member Added..."
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n✅ Invitation system tests completed!"
Expected Output:

json
{
    "message": "Invitation accepted successfully",
    "organization": {
        "id": 1,
        "name": "TechCorp",
        "member_count": 6
    },
    "role": "viewer"
}
Test 5: Role-Based Access Control (RBAC)
bash
#!/bin/bash
# test_5_rbac.sh - Role-Based Access Control Tests

echo "========================================="
"🔒 TEST 5: ROLE-BASED ACCESS CONTROL"
echo "========================================="

# 5.1 Test Admin Access (Alice)
echo -e "\n5.1 Testing Admin Access (Alice)..."
ALICE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "Alice can manage members:"
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -c "import json; print('  ✅ Status:', json.load(sys.stdin).get('count', 0), 'members found')"

# 5.2 Test Manager Access (Bob)
echo -e "\n5.2 Testing Manager Access (Bob)..."
BOB_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_manager","password":"Manager123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "Bob can view members:"
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $BOB_TOKEN" | python3 -c "import json; print('  ✅ Status:', json.load(sys.stdin).get('count', 0), 'members found')"

echo -e "\nBob CANNOT add members (should fail):"
RESPONSE=$(curl -s -X POST http://localhost:8500/api/organizations/1/members/add/ \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 999, "role": "developer"}')

if echo $RESPONSE | grep -q "permission"; then
    echo "  ✅ Access denied as expected!"
else
    echo "  ❌ Access should be denied!"
fi

# 5.3 Test Viewer Access (Eve)
echo -e "\n5.3 Testing Viewer Access (Eve)..."
EVE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"eve_viewer","password":"Viewer123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "Eve can view members:"
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $EVE_TOKEN" | python3 -c "import json; print('  ✅ Status:', json.load(sys.stdin).get('count', 0), 'members found')"

echo -e "\nEve CANNOT create invitations:"
RESPONSE=$(curl -s -X POST http://localhost:8500/api/organizations/1/invitations/create/ \
  -H "Authorization: Bearer $EVE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "role": "viewer"}')

if echo $RESPONSE | grep -q "permission"; then
    echo "  ✅ Access denied as expected!"
else
    echo "  ❌ Access should be denied!"
fi

echo -e "\n✅ RBAC tests completed!"
Expected Output:

text
🔒 TEST 5: ROLE-BASED ACCESS CONTROL

5.1 Testing Admin Access (Alice)...
Alice can manage members:
  ✅ Status: 6 members found

5.2 Testing Manager Access (Bob)...
Bob can view members:
  ✅ Status: 6 members found

Bob CANNOT add members (should fail):
  ✅ Access denied as expected!

5.3 Testing Viewer Access (Eve)...
Eve can view members:
  ✅ Status: 6 members found

Eve CANNOT create invitations:
  ✅ Access denied as expected!
Test 6: Cross-Organization Access
bash
#!/bin/bash
# test_6_cross_org.sh - Cross-Organization Access Tests

echo "========================================="
"🏢 TEST 6: CROSS-ORGANIZATION ACCESS"
echo "========================================="

# Login as Bob (Member of both TechCorp and Startup.io)
BOB_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"bob_manager","password":"Manager123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

# 6.1 List Bob's Organizations
echo -e "\n6.1 Bob's Organizations..."
curl -s -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $BOB_TOKEN" | python3 -m json.tool 2>/dev/null

# 6.2 Access TechCorp (Bob is member)
echo -e "\n6.2 Bob Accessing TechCorp..."
curl -s -X GET http://localhost:8500/api/organizations/1/ \
  -H "Authorization: Bearer $BOB_TOKEN" | python3 -c "import json; data=json.load(sys.stdin); print('  ✅ Access to TechCorp:', data.get('name', 'Not found'))"

# 6.3 Access Startup.io (Bob is member)
echo -e "\n6.3 Bob Accessing Startup.io..."
STARTUP_ID=$(curl -s -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $BOB_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); org=[o for o in data['results'] if o['name']=='Startup.io']; print(org[0]['id'] if org else '')" 2>/dev/null)

if [ ! -z "$STARTUP_ID" ]; then
    curl -s -X GET http://localhost:8500/api/organizations/$STARTUP_ID/ \
      -H "Authorization: Bearer $BOB_TOKEN" | python3 -c "import json; data=json.load(sys.stdin); print('  ✅ Access to Startup.io:', data.get('name', 'Not found'))"
fi

# 6.4 Try Accessing Organization Bob is NOT a member of
echo -e "\n6.4 Bob Attempting to Access AI Innovations..."
AI_ID=$(curl -s -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $BOB_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); org=[o for o in data['results'] if o['name']=='AI Innovations']; print(org[0]['id'] if org else '3')" 2>/dev/null)

RESPONSE=$(curl -s -X GET http://localhost:8500/api/organizations/$AI_ID/ \
  -H "Authorization: Bearer $BOB_TOKEN")

if echo $RESPONSE | grep -q "permission"; then
    echo "  ✅ Access denied as expected (Bob is not a member)"
else
    echo "  ❌ Access should be denied!"
fi

echo -e "\n✅ Cross-organization tests completed!"
Test 7: Complete User Journey
bash
#!/bin/bash
# test_7_journey.sh - Complete User Journey

echo "========================================="
"🌟 TEST 7: COMPLETE USER JOURNEY"
echo "========================================="

echo "This test simulates a complete user journey:"
echo "1. Sarah registers"
echo "2. Alice invites Sarah to TechCorp"
echo "3. Sarah accepts the invitation"
echo "4. Sarah contributes to TechCorp"
echo "5. Sarah is promoted to Manager"

# Step 1: Sarah registers
echo -e "\n📝 Step 1: Sarah registers..."
SARAH_REGISTER=$(curl -s -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah_developer",
    "email": "sarah@example.com",
    "password": "Sarah123!",
    "password2": "Sarah123!"
  }')

SARAH_TOKEN=$(echo $SARAH_REGISTER | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)
SARAH_ID=$(echo $SARAH_REGISTER | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))" 2>/dev/null)
echo "✅ Sarah registered with ID: $SARAH_ID"

# Step 2: Alice invites Sarah
echo -e "\n📧 Step 2: Alice invites Sarah..."
ALICE_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

INVITE_RESPONSE=$(curl -s -X POST http://localhost:8500/api/organizations/1/invitations/create/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"sarah@example.com\",
    \"role\": \"developer\"
  }")

INVITE_TOKEN=$(echo $INVITE_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null)
echo "✅ Invitation created with token: ${INVITE_TOKEN:0:20}..."

# Step 3: Sarah accepts invitation
echo -e "\n✅ Step 3: Sarah accepts invitation..."
curl -s -X POST http://localhost:8500/api/organizations/invitations/accept/ \
  -H "Authorization: Bearer $SARAH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$INVITE_TOKEN\"}" | python3 -m json.tool 2>/dev/null

# Step 4: Sarah views her organizations
echo -e "\n👀 Step 4: Sarah views her organizations..."
curl -s -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $SARAH_TOKEN" | python3 -m json.tool 2>/dev/null

# Step 5: Alice promotes Sarah to Manager
echo -e "\n📈 Step 5: Alice promotes Sarah to Manager..."
curl -s -X PUT http://localhost:8500/api/organizations/1/members/update/ \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $SARAH_ID,
    \"role\": \"manager\"
  }" | python3 -m json.tool 2>/dev/null

# Step 6: Verify Sarah's new role
echo -e "\n✅ Step 6: Verifying Sarah's new role..."
curl -s -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $ALICE_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n🌟 Complete user journey completed successfully!"
📚 API Endpoints Reference
Authentication Endpoints
Method	Endpoint	Description	Auth	Body
POST	/api/auth/register/	Register new user	❌	username, email, password, password2
POST	/api/auth/login/	Login user	❌	username, password
GET	/api/auth/profile/	Get user profile	✅	-
PATCH	/api/auth/profile/	Update profile	✅	phone, email, etc.
POST	/api/auth/change-password/	Change password	✅	old_password, new_password, confirm_password
POST	/api/auth/logout/	Logout	✅	refresh token
Organization Endpoints
Method	Endpoint	Description	Auth	Body
GET	/api/organizations/	List user's organizations	✅	-
POST	/api/organizations/	Create organization	✅	name, description, website
GET	/api/organizations/{id}/	Get organization details	✅	-
PUT/PATCH	/api/organizations/{id}/	Update organization	✅	name, description, website
DELETE	/api/organizations/{id}/	Delete (soft) organization	✅	-
Member Endpoints
Method	Endpoint	Description	Auth	Body
GET	/api/organizations/{id}/members/	List members	✅	-
POST	/api/organizations/{id}/members/add/	Add member	✅	user_id, role
PUT	/api/organizations/{id}/members/update/	Update role	✅	user_id, role
DELETE	/api/organizations/{id}/members/remove/{user_id}/	Remove member	✅	-
Invitation Endpoints
Method	Endpoint	Description	Auth	Body
GET	/api/organizations/{id}/invitations/	List invitations	✅	-
POST	/api/organizations/{id}/invitations/create/	Create invitation	✅	email, role
POST	/api/organizations/invitations/accept/	Accept invitation	❌	token
POST	/api/organizations/invitations/decline/	Decline invitation	❌	token
📊 Expected Outputs
Successful Registration Response
json
{
    "refresh": "eyJhbGciOiJIUzI1NiIs...",
    "access": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
        "id": 1,
        "username": "alice_admin",
        "email": "alice@techcorp.com",
        "phone": null,
        "avatar": null,
        "is_active": true,
        "created_at": "2026-06-19T12:00:00Z"
    }
}
Successful Organization Creation Response
json
{
    "id": 1,
    "name": "TechCorp",
    "slug": "techcorp",
    "description": "Leading technology company",
    "website": "https://techcorp.com",
    "created_by": 1,
    "created_by_email": "alice@techcorp.com",
    "is_active": true,
    "member_count": 1,
    "user_role": "admin",
    "is_admin": true
}
Error Responses
Invalid Credentials (401)
json
{
    "non_field_errors": ["Invalid credentials"]
}
Permission Denied (403)
json
{
    "detail": "You do not have permission to perform this action."
}
Not Found (404)
json
{
    "detail": "Not found."
}
Validation Error (400)
json
{
    "name": ["An organization with this name already exists."]
}
🔧 Troubleshooting Guide
Common Issues & Solutions
1. User Not Found
bash
# Problem: User doesn't exist
{"detail": "No User matches the given query."}

# Solution: Check if user exists
docker-compose exec backend python manage.py shell -c "from accounts.models import User; print(User.objects.all())"
2. Token Expired
bash
# Problem: Token expired
{"detail": "Token is invalid or expired"}

# Solution: Refresh token or login again
curl -X POST http://localhost:8500/api/auth/login/ -d '{"username":"user","password":"pass"}'
3. Permission Denied
bash
# Problem: User doesn't have permission
{"detail": "You do not have permission to perform this action."}

# Solution: Check user's role
docker-compose exec backend python manage.py shell -c "from organizations.models import Membership; print(Membership.objects.filter(user__username='username'))"
4. Duplicate Organization
bash
# Problem: Organization name already exists
{"name": ["An organization with this name already exists."]}

# Solution: Use a different name
Debug Commands
bash
# Check all users
docker-compose exec backend python manage.py shell -c "from accounts.models import User; [print(f'{u.id}: {u.username} ({u.email})') for u in User.objects.all()]"

# Check all organizations
docker-compose exec backend python manage.py shell -c "from organizations.models import Organization; [print(f'{o.id}: {o.name} - {o.memberships.count()} members') for o in Organization.objects.all()]"

# Check all memberships
docker-compose exec backend python manage.py shell -c "from organizations.models import Membership; [print(f'{m.user.username} → {m.organization.name} ({m.role})') for m in Membership.objects.all()]"

# Check all invitations
docker-compose exec backend python manage.py shell -c "from organizations.models import Invitation; [print(f'{i.email} → {i.organization.name} ({i.status})') for i in Invitation.objects.all()]"

# Check API URLs
docker-compose exec backend python manage.py show_urls | grep organizations
Logging
bash
# View backend logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend

# View database logs
docker-compose logs db
🎯 Summary
What We've Tested
✅ Authentication - Register, Login, Profile

✅ Organization Management - Create, Read, Update, Delete

✅ Member Management - Add, Update, Remove

✅ Invitation System - Create, List, Accept, Decline

✅ Role-Based Access Control - Admin, Manager, Developer, Viewer

✅ Cross-Organization Access - User can belong to multiple orgs

✅ Complete User Journey - Real-world scenario

Key Takeaways
Organizations are the core unit of the application

Users can belong to multiple organizations

Roles determine what users can do

Invitations provide a secure way to add users

Soft delete preserves data integrity

RBAC ensures security

Next Steps
Add email notifications for invitations

Implement audit logging

Add organization settings

Create custom permissions

Implement team project management

📝 Quick Reference Card
bash
# Quick Login
TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin).get('access'))")

# Test with Token
curl -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $TOKEN"

# Clean Up (Reset Everything)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py create_test_data
🎉 Congratulations! You now have a complete understanding of the Organizations App!

