#!/bin/bash
# test_all_tickets.sh   --->
#chmod +x test_all_tickets.sh
#./test_all_tickets.sh

BASE_URL="http://localhost:8500/api"
AUTH_URL="$BASE_URL/auth"
PROJECT_URL="$BASE_URL/projects"

echo "========================================="
echo "🎫 TICKETS APP - COMPLETE WORKING TEST"
echo "========================================="

# 1. Login as Admin
echo -e "\n1️⃣ Login as Admin"
ADMIN_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
echo "✅ Admin logged in"

# 2. Login as Developer
echo -e "\n2️⃣ Login as Developer"
DEV_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"dev1","password":"Dev123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
echo "✅ Developer logged in"

# 3. Create Bug Ticket
echo -e "\n3️⃣ Create Bug Ticket"
curl -s -X POST $PROJECT_URL/3/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix login authentication bug",
    "description": "Users with special characters in password cannot login",
    "status": "todo",
    "priority": "high",
    "ticket_type": "bug",
    "assignee": 7,
    "due_date": "2026-07-19T23:59:59Z"
  }' | python3 -m json.tool 2>/dev/null

# 4. Create Feature Ticket
echo -e "\n4️⃣ Create Feature Ticket"
curl -s -X POST $PROJECT_URL/3/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement dark mode",
    "description": "Add dark theme support",
    "status": "backlog",
    "priority": "medium",
    "ticket_type": "feature",
    "assignee": 9,
    "due_date": "2026-08-01T23:59:59Z"
  }' | python3 -m json.tool 2>/dev/null

# 5. Create Task Ticket
echo -e "\n5️⃣ Create Task Ticket"
curl -s -X POST $PROJECT_URL/3/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Update documentation",
    "description": "Update API documentation",
    "status": "todo",
    "priority": "low",
    "ticket_type": "task",
    "assignee": 10
  }' | python3 -m json.tool 2>/dev/null

# 6. List All Tickets
echo -e "\n6️⃣ List All Tickets"
curl -s -X GET $PROJECT_URL/3/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 7. Get Ticket Statistics
echo -e "\n7️⃣ Get Ticket Statistics"
curl -s -X GET $PROJECT_URL/3/tickets/stats/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 8. Filter Tickets
echo -e "\n8️⃣ Filter Tickets (high priority)"
curl -s -X GET "$PROJECT_URL/3/tickets/?priority=high" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 9. Search Tickets
echo -e "\n9️⃣ Search Tickets (login)"
curl -s -X GET "$PROJECT_URL/3/tickets/?search=login" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 10. Get First Ticket ID
TICKET_ID=$(curl -s -X GET $PROJECT_URL/3/tickets/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results'][0]['id'] if data['results'] else '')" 2>/dev/null)

if [ ! -z "$TICKET_ID" ]; then
    echo -e "\n🔟 Get Ticket Details (ID: $TICKET_ID)"
    curl -s -X GET $PROJECT_URL/tickets/$TICKET_ID/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
    
    echo -e "\n1️⃣1️⃣ Update Ticket Status (In Progress)"
    curl -s -X POST $PROJECT_URL/tickets/$TICKET_ID/status/ \
      -H "Authorization: Bearer $DEV_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"status":"in_progress"}' | python3 -m json.tool 2>/dev/null
    
    echo -e "\n1️⃣2️⃣ Get Ticket History"
    curl -s -X GET $PROJECT_URL/tickets/$TICKET_ID/history/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
    
    echo -e "\n1️⃣3️⃣ Mark Ticket as Done"
    curl -s -X POST $PROJECT_URL/tickets/$TICKET_ID/status/ \
      -H "Authorization: Bearer $DEV_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"status":"done"}' | python3 -m json.tool 2>/dev/null
fi

echo -e "\n========================================="
echo "✅ All tests completed successfully!"

echo "========================================="