1. Login to Get Token (Fixed)
bash
# Login with username (since your User model uses username as default)
curl -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}'

# OR if you have email authentication implemented
curl -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test@example.com","password":"TestPass123"}'
2. Save Token for Reuse
bash
# Login and save token to variable
TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "Your token: $TOKEN"
3. Create an Organization
bash
curl -X POST http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My SaaS Company",
    "description": "Building awesome products",
    "website": "https://example.com"
  }'
4. List Organizations
bash
curl -X GET http://localhost:8500/api/organizations/ \
  -H "Authorization: Bearer $TOKEN"
5. Get Organization Details
bash
curl -X GET http://localhost:8500/api/organizations/1/ \
  -H "Authorization: Bearer $TOKEN"
6. List Members
bash
curl -X GET http://localhost:8500/api/organizations/1/members/ \
  -H "Authorization: Bearer $TOKEN"
7. Add a Member
bash
# Register a new user first
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8500/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"newuser@example.com","password":"TestPass123","password2":"TestPass123"}')

# Get the new user's ID
USER_ID=$(echo $REGISTER_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))" 2>/dev/null)

# Add member
curl -X POST http://localhost:8500/api/organizations/1/members/add/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"role\": \"developer\"
  }"
8. Update Member Role
bash
curl -X PUT http://localhost:8500/api/organizations/1/members/update/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "role": "manager"
  }'
9. Remove Member
bash
curl -X DELETE http://localhost:8500/api/organizations/1/members/remove/2/ \
  -H "Authorization: Bearer $TOKEN"
10. Create Invitation
bash
curl -X POST http://localhost:8500/api/organizations/1/invitations/create/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invited@example.com",
    "role": "viewer"
  }'
11. List Invitations
bash
curl -X GET http://localhost:8500/api/organizations/1/invitations/ \
  -H "Authorization: Bearer $TOKEN"
Complete Test Script
Here's a complete bash script that tests everything:

bash
#!/bin/bash
# test_organizations.sh

BASE_URL="http://localhost:8500/api"
AUTH_URL="$BASE_URL/auth"
ORG_URL="$BASE_URL/organizations"

echo "========================================="
echo "1. Register First User (Admin)"
echo "========================================="
REGISTER1=$(curl -s -X POST $AUTH_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"orgadmin","email":"admin@org.com","password":"TestPass123","password2":"TestPass123"}')

echo $REGISTER1 | python3 -m json.tool 2>/dev/null
ADMIN_TOKEN=$(echo $REGISTER1 | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" = "null" ]; then
    echo "❌ Registration failed"
    exit 1
fi
echo "✅ Admin token: ${ADMIN_TOKEN:0:50}..."

echo -e "\n========================================="
echo "2. Register Second User (Member)"
echo "========================================="
REGISTER2=$(curl -s -X POST $AUTH_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"devuser","email":"dev@example.com","password":"TestPass123","password2":"TestPass123"}')

echo $REGISTER2 | python3 -m json.tool 2>/dev/null
MEMBER_TOKEN=$(echo $REGISTER2 | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)
MEMBER_ID=$(echo $REGISTER2 | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))" 2>/dev/null)

echo "✅ Member created with ID: $MEMBER_ID"

echo -e "\n========================================="
echo "3. Create Organization"
echo "========================================="
ORG_RESPONSE=$(curl -s -X POST $ORG_URL/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Corp",
    "description": "Leading technology company",
    "website": "https://techcorp.com"
  }')

echo $ORG_RESPONSE | python3 -m json.tool 2>/dev/null
ORG_ID=$(echo $ORG_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null)

if [ -z "$ORG_ID" ] || [ "$ORG_ID" = "null" ]; then
    echo "❌ Organization creation failed"
    exit 1
fi
echo "✅ Organization created with ID: $ORG_ID"

echo -e "\n========================================="
echo "4. List Organizations"
echo "========================================="
curl -s -X GET $ORG_URL/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "5. Get Organization Details"
echo "========================================="
curl -s -X GET $ORG_URL/$ORG_ID/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "6. Add Member to Organization"
echo "========================================="
ADD_MEMBER=$(curl -s -X POST $ORG_URL/$ORG_ID/members/add/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $MEMBER_ID,
    \"role\": \"developer\"
  }")

echo $ADD_MEMBER | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "7. List Members"
echo "========================================="
curl -s -X GET $ORG_URL/$ORG_ID/members/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "8. Update Member Role"
echo "========================================="
curl -s -X PUT $ORG_URL/$ORG_ID/members/update/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $MEMBER_ID,
    \"role\": \"manager\"
  }" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "9. Create Invitation"
echo "========================================="
INVITE_RESPONSE=$(curl -s -X POST $ORG_URL/$ORG_ID/invitations/create/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invited@example.com",
    "role": "viewer"
  }')

echo $INVITE_RESPONSE | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "10. List Invitations"
echo "========================================="
curl -s -X GET $ORG_URL/$ORG_ID/invitations/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "11. Test Member Access (Member tries to update admin)"
echo "========================================="
# This should fail because member is not admin
curl -s -X PUT $ORG_URL/$ORG_ID/members/update/ \
  -H "Authorization: Bearer $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": 1,
    \"role\": \"admin\"
  }" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "12. Remove Member"
echo "========================================="
REMOVE_MEMBER=$(curl -s -X DELETE $ORG_URL/$ORG_ID/members/remove/$MEMBER_ID/ \
  -H "Authorization: Bearer $ADMIN_TOKEN")

echo $REMOVE_MEMBER | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "✅ Tests completed!"
echo "========================================="
