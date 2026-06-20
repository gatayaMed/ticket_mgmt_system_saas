# Get admin token
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

# Create a project
curl -X POST http://localhost:8500/api/organizations/1/projects/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Test Project",
    "description":"This is a test project",
    "status":"active",
    "priority":"high",
    "organization":1
  }' | python3 -m json.tool

# List projects
curl -X GET http://localhost:8500/api/organizations/1/projects/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
  ------------------------------


  OUTPUT: 
  ADMIN_TOKEN=$(curl -s -X POST http://localhost:8500/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
med@gataya-med:~/Desktop/Projects/Saas_ticket_mgmt_system$ curl -X POST http://localhost:8500/api/organizations/1/projects/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Test Project",
    "description":"This is a test project",
    "status":"active",
    "priority":"high",
    "organization":1
  }' | python3 -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   291  100   148  100   143   2140   2068 --:--:-- --:--:-- --:--:--  4157
{
    "name": "Test Project",
    "description": "This is a test project",
    "status": "active",
    "priority": "high",
    "start_date": null,
    "end_date": null,
    "due_date": null
}
med@gataya-med:~/Desktop/Projects/Saas_ticket_mgmt_system$ curl -X GET http://localhost:8500/api/organizations/1/projects/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1143  100  1143    0     0  17856      0 --:--:-- --:--:-- --:--:-- 18142
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 3,
            "name": "Test Project",
            "description": "This is a test project",
            "slug": "test-project-1",
            "organization": 1,
            "organization_name": "My SaaS Company",
            "status": "active",
            "status_display": "Active",
            "priority": "high",
            "priority_display": "High",
            "start_date": null,
            "end_date": null,
            "due_date": null,
            "created_by": 1,
            "created_by_email": "test@example.com",
            "created_by_username": "testuser",
            "created_at": "2026-06-19T15:01:38.269394Z",
            "updated_at": "2026-06-19T15:01:38.291308Z",
            "is_active": true,
            "progress": 0,
            "member_count": 1,
            "is_overdue": false,
            "days_remaining": null
        },
        {
            "id": 1,
            "name": "Test Project",
            "description": "Test description",
            "slug": "test-project",
            "organization": 1,
            "organization_name": "My SaaS Company",
            "status": "active",
            "status_display": "Active",
            "priority": "medium",
            "priority_display": "Medium",
            "start_date": null,
            "end_date": null,
            "due_date": null,
            "created_by": 1,
            "created_by_email": "test@example.com",
            "created_by_username": "testuser",
            "created_at": "2026-06-19T14:53:58.542811Z",
            "updated_at": "2026-06-19T14:53:58.563396Z",
            "is_active": true,
            "progress": 150,
            "member_count": 0,
            "is_overdue": false,
            "days_remaining": null
        }
    ]
}
