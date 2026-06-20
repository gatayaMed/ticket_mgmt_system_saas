#!/bin/bash
# test_project_create.sh

# Login as Alice (Admin)
TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_admin","password":"Admin123!"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

echo "✅ Logged in as Alice"

# Create a project
curl -X POST http://localhost:8500/api/organizations/1/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SaaS Platform Development",
    "description": "Building our core SaaS platform",
    "priority": "high",
    "start_date": "2026-06-20T09:00:00Z",
    "due_date": "2026-12-31T23:59:59Z"
  }' | python3 -m json.tool 2>/dev/null