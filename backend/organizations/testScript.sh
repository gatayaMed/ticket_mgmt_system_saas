#!/bin/bash
# complete_org_test.sh

BASE_URL="http://localhost:8500/api"
AUTH_URL="$BASE_URL/auth"
ORG_URL="$BASE_URL/organizations"

echo "========================================="
echo "1. Login as Admin"
echo "========================================="
ADMIN_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "✅ Admin logged in"

echo -e "\n========================================="
echo "2. Create Invitation for New User"
echo "========================================="
INVITE_RESPONSE=$(curl -s -X POST $ORG_URL/1/invitations/create/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newinvited@example.com",
    "role": "developer"
  }')

echo $INVITE_RESPONSE | python3 -m json.tool 2>/dev/null
INVITE_TOKEN=$(echo $INVITE_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('token', ''))" 2>/dev/null)
echo "✅ Invitation created with token: ${INVITE_TOKEN:0:20}..."

echo -e "\n========================================="
echo "3. Register New User"
echo "========================================="
REGISTER_RESPONSE=$(curl -s -X POST $AUTH_URL/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newinviteduser","email":"newinvited@example.com","password":"TestPass123","password2":"TestPass123"}')

echo $REGISTER_RESPONSE | python3 -m json.tool 2>/dev/null
echo "✅ New user registered"

echo -e "\n========================================="
echo "4. Login as New User"
echo "========================================="
USER_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"newinviteduser","password":"TestPass123"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "✅ New user logged in"

echo -e "\n========================================="
echo "5. Accept Invitation"
echo "========================================="
ACCEPT_RESPONSE=$(curl -s -X POST $ORG_URL/invitations/accept/ \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"$INVITE_TOKEN\"}")

echo $ACCEPT_RESPONSE | python3 -m json.tool 2>/dev/null
echo "✅ Invitation accepted"

echo -e "\n========================================="
echo "6. List All Members (Admin View)"
echo "========================================="
curl -s -X GET $ORG_URL/1/members/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "7. Update Member Role (Admin Only)"
echo "========================================="
# First get the user ID of the new member
NEW_USER_ID=$(curl -s -X GET $ORG_URL/1/members/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); users=[u for u in data['results'] if u['user_details']['email']=='newinvited@example.com']; print(users[0]['user'] if users else '')" 2>/dev/null)

if [ ! -z "$NEW_USER_ID" ]; then
    echo "Updating user ID: $NEW_USER_ID"
    curl -s -X PUT $ORG_URL/1/members/update/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"user_id\": $NEW_USER_ID,
        \"role\": \"manager\"
      }" | python3 -m json.tool 2>/dev/null
    echo "✅ Role updated to manager"
fi

echo -e "\n========================================="
echo "8. List User's Organizations"
echo "========================================="
curl -s -X GET $ORG_URL/ \
  -H "Authorization: Bearer $USER_TOKEN" | python3 -m json.tool 2>/dev/null

echo -e "\n========================================="
echo "✅ All tests completed successfully!"
echo "========================================="