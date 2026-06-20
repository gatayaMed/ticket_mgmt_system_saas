#!/bin/bash
# test_comments_fixed.sh

BASE_URL="http://localhost:8500/api"
AUTH_URL="$BASE_URL/auth"

echo "========================================="
echo "💬 COMMENTS APP - FIXED TEST"
echo "========================================="

# 1. Login as Admin
echo -e "\n1️⃣ Login as Admin"
ADMIN_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

echo "✅ Admin logged in"

# 2. Create a Comment
echo -e "\n2️⃣ Create Comment on Ticket 1"
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/tickets/1/comments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a critical issue that needs immediate attention"
  }')

echo $CREATE_RESPONSE | python3 -m json.tool 2>/dev/null

# Extract comment ID
COMMENT_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ ! -z "$COMMENT_ID" ]; then
    echo "✅ Comment created with ID: $COMMENT_ID"
    
    # 3. List All Comments
    echo -e "\n3️⃣ List All Comments on Ticket 1"
    curl -s -X GET $BASE_URL/tickets/1/comments/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
    
    # 4. Get Comment Details
    echo -e "\n4️⃣ Get Comment Details"
    curl -s -X GET $BASE_URL/comments/$COMMENT_ID/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
    
    # 5. Edit Comment
    echo -e "\n5️⃣ Edit Comment"
    curl -s -X PATCH $BASE_URL/comments/$COMMENT_ID/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "content": "Updated: This is critical and I will escalate to the team lead"
      }' | python3 -m json.tool 2>/dev/null
    
    # 6. Delete Comment (Soft Delete)
    echo -e "\n6️⃣ Delete Comment"
    curl -s -X DELETE $BASE_URL/comments/$COMMENT_ID/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
    
    # 7. Verify Comment is Gone
    echo -e "\n7️⃣ Verify Comment is Deleted"
    curl -s -X GET $BASE_URL/tickets/1/comments/ \
      -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null
else
    echo "❌ Failed to create comment"
fi

echo -e "\n========================================="
echo "✅ Tests completed!"
echo "========================================="