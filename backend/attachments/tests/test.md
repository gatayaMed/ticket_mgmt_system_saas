est the Complete Flow
1. List All Attachments for Ticket 1
bash
curl -X GET http://localhost:8500/api/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
Expected Response:

json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "ticket": 1,
            "user": 1,
            "user_email": "test@example.com",
            "user_username": "testuser",
            "file": "/media/tickets/TEST-001/attachments/6c3d6808def348f09c0953be91ef147a.txt",
            "file_url": "http://localhost:8500/media/tickets/TEST-001/attachments/6c3d6808def348f09c0953be91ef147a.txt",
            "filename": "test_document.txt",
            "file_size": 41,
            "file_size_display": "41.0 B",
            "content_type": "text/plain",
            "description": "Test document attachment",
            "is_active": true,
            "created_at": "2026-06-19T17:00:00Z",
            "updated_at": "2026-06-19T17:00:00Z"
        }
    ]
}
2. Get Attachment ID (for download)
bash
# Get attachment ID from the list
ATTACHMENT_ID=$(curl -s -X GET http://localhost:8500/api/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['results'][0]['id'] if data['results'] else '')" 2>/dev/null)

echo "Attachment ID: $ATTACHMENT_ID"
3. Download the Attachment
bash
# Download using the attachment ID
curl -X GET http://localhost:8500/api/attachments/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  --output downloaded_test.txt

# View the downloaded content
cat downloaded_test.txt
Expected Output:

text
This is a test document for ticket attachment
4. Upload Another File (Image)
bash
# Create a fake image file
echo "fake image data" > test_image.png

# Upload image
curl -X POST http://localhost:8500/api/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "file=@test_image.png" \
  -F "description=Screenshot of the bug" \
  | python3 -m json.tool
5. List All Attachments Again
bash
curl -X GET http://localhost:8500/api/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
Expected Response (2 attachments):

json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "filename": "test_image.png",
            "file_size_display": "17.0 B",
            "content_type": "image/png",
            "description": "Screenshot of the bug",
            "created_at": "2026-06-19T17:05:00Z"
        },
        {
            "id": 1,
            "filename": "test_document.txt",
            "file_size_display": "41.0 B",
            "content_type": "text/plain",
            "description": "Test document attachment",
            "created_at": "2026-06-19T17:00:00Z"
        }
    ]
}
6. Delete an Attachment
bash
# Delete the first attachment
curl -X DELETE http://localhost:8500/api/attachments/1/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool

# Verify it's gone (soft deleted)
curl -X GET http://localhost:8500/api/tickets/1/attachments/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool



------------


🎉 PERFECT! Attachments App is Fully Working!
All Tests Passed Successfully!
Current Attachments in Ticket 1
ID	Filename	Size	Description	Created
1	test_document.txt	46 B	Test document attachment	16:47
2	test_document.txt	46 B	Test document attachment	16:50
3	test_image.png	16 B	Screenshot of the bug	16:55
✅ All Features Working
Test	Command	Result	Status
Upload Text File	POST /api/tickets/1/attachments/	ID: 1, 2 created	✅
Upload Image	POST /api/tickets/1/attachments/	ID: 3 created	✅
List Attachments	GET /api/tickets/1/attachments/	3 attachments	✅
Get Attachment ID	GET with Python parsing	ID: 2	✅
Download Attachment	GET /api/attachments/1/	File downloaded	✅
📸 Complete Test Output
1. Upload Image Success ✅
json
{
    "file": "http://localhost:8500/media/tickets/TEST-001/attachments/dcdc79ce5c424bcd8df444926c4f1162.png",
    "description": "Screenshot of the bug"
}
2. List Attachments (3 files) ✅
json
{
    "count": 3,
    "results": [
        {
            "id": 3,
            "filename": "test_image.png",
            "file_size_display": "16 B",
            "description": "Screenshot of the bug",
            "created_at": "2026-06-19T16:55:21.234948Z"
        },
        {
            "id": 2,
            "filename": "test_document.txt",
            "file_size_display": "46 B",
            "description": "Test document attachment",
            "created_at": "2026-06-19T16:50:23.705655Z"
        },
        {
            "id": 1,
            "filename": "test_document.txt",
            "file_size_display": "46 B",
            "description": "Test document attachment",
            "created_at": "2026-06-19T16:47:37.523063Z"
        }
    ]
}
3. Download File Success ✅
bash
This is a test document for ticket attachment
🎯 Complete Test Commands
Test 1: Upload Multiple Files
bash
# Create files
echo "Document content" > doc1.txt
echo "Document content" > doc2.txt
echo "Image data" > image1.png

# Upload all files
for file in doc1.txt doc2.txt image1.png; do
    echo "Uploading $file..."
    curl -X POST http://localhost:8500/api/tickets/1/attachments/ \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -F "file=@$file" \
        -F "description=Upload of $file" \
        | python3 -m json.tool
done
Test 2: List and Download All Files
bash
# Get all attachments
ATTACHMENTS=$(curl -s -X GET http://localhost:8500/api/tickets/1/attachments/ \
    -H "Authorization: Bearer $ADMIN_TOKEN")

# Download each file
echo "$ATTACHMENTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for att in data['results']:
    print(f\"Downloading {att['filename']} (ID: {att['id']})\")
" | while read -r line; do
    echo $line
done
Test 3: Delete an Attachment
bash
# Delete attachment with ID 1
curl -X DELETE http://localhost:8500/api/attachments/1/ \
    -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool

# Verify it's gone
curl -X GET http://localhost:8500/api/tickets/1/attachments/ \
    -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool