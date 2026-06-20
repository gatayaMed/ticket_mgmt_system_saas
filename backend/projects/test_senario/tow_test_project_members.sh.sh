#!/bin/bash
# test_project_members.sh

# Login as Alice (Admin)
TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

# Get Charlie's user ID
CHARLIE_ID=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"charlie_dev","password":"Dev123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', ''))" 2>/dev/null)

# Add Charlie to project
curl -X POST http://localhost:8500/api/projects/1/members/add/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $CHARLIE_ID,
    \"role\": \"developer\"
  }" | python3 -m json.tool 2>/dev/null