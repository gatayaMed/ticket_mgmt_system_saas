#!/bin/bash
# test_attachments_complete.sh
#chmod +x test_attachments_complete.sh
#./test_attachments_complete.sh

BASE_URL="http://localhost:8500/api"
AUTH_URL="$BASE_URL/auth"

echo "========================================="
echo "📎 ATTACHMENTS APP - COMPLETE TESTING"
echo "========================================="

# 1. Login as Admin
echo -e "\n1️⃣ Login as Admin"
ADMIN_TOKEN=$(curl -s -X POST $AUTH_URL/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

echo "✅ Admin logged in"

# 2. Create test files
echo -e "\n2️⃣ Creating test files"
echo "This is a test document for ticket attachment" > test_document.txt
echo "fake image data" > test_image.png

# 3. Upload text file
echo -e "\n3️⃣ Upload Text File"
UPLOAD_RESPONSE=$(curl -s -X POST $BASE_URL/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_document.txt" \
  -F "description=Test document attachment")

echo $UPLOAD_RESPONSE | python3 -m json.tool 2>/dev/null

# Extract attachment ID
ATTACHMENT_ID=$(echo $UPLOAD_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ ! -z "$ATTACHMENT_ID" ]; then
    echo "✅ First attachment uploaded with ID: $ATTACHMENT_ID"
else
    echo "❌ Failed to upload first attachment"
    exit 1
fi

# 4. Upload image file
echo -e "\n4️⃣ Upload Image File"
UPLOAD_RESPONSE2=$(curl -s -X POST $BASE_URL/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_image.png" \
  -F "description=Screenshot of the bug")

echo $UPLOAD_RESPONSE2 | python3 -m json.tool 2>/dev/null
ATTACHMENT_ID2=$(echo $UPLOAD_RESPONSE2 | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ ! -z "$ATTACHMENT_ID2" ]; then
    echo "✅ Second attachment uploaded with ID: $ATTACHMENT_ID2"
fi

# 5. List all attachments
echo -e "\n5️⃣ List All Attachments"
curl -s -X GET $BASE_URL/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 6. Download first attachment
echo -e "\n6️⃣ Download First Attachment"
curl -s -X GET $BASE_URL/attachments/$ATTACHMENT_ID/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o downloaded_test.txt

if [ -f "downloaded_test.txt" ]; then
    echo "✅ File downloaded successfully"
    echo "Content:"
    cat downloaded_test.txt
    rm downloaded_test.txt
else
    echo "❌ Failed to download file"
fi

# 7. Delete first attachment
echo -e "\n7️⃣ Delete First Attachment"
curl -s -X DELETE $BASE_URL/attachments/$ATTACHMENT_ID/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# 8. Verify deletion
echo -e "\n8️⃣ Verify Attachment is Deleted"
curl -s -X GET $BASE_URL/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool 2>/dev/null

# Clean up
rm -f test_document.txt test_image.png

echo -e "\n========================================="
echo "✅ All tests completed successfully!"
echo "========================================="