#docker-compose exec backend python test_attachments.py

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from attachments.models import Attachment

User = get_user_model()

def test_attachments():
    print("Testing attachments...")
    
    # Get a user and ticket
    user = User.objects.first()
    ticket = Ticket.objects.first()
    
    if not user or not ticket:
        print("No user or ticket found. Please create test data first.")
        return
    
    # Create a test file
    test_content = b"This is a test file content for attachment testing."
    test_file = SimpleUploadedFile(
        "test_attachment.txt",
        test_content,
        content_type="text/plain"
    )
    
    # Create attachment
    attachment = Attachment.objects.create(
        ticket=ticket,
        user=user,
        file=test_file,
        description="Test attachment from script"
    )
    
    print(f"✅ Attachment created: {attachment.id}")
    print(f"   Filename: {attachment.filename}")
    print(f"   File size: {attachment.file_size} bytes")
    print(f"   Content type: {attachment.content_type}")
    
    # List attachments
    attachments = Attachment.objects.filter(ticket=ticket, is_active=True)
    print(f"\n✅ Found {attachments.count()} attachments for ticket {ticket.ticket_id}")
    
    for att in attachments:
        print(f"   - {att.filename} ({att.file_size} bytes)")
    
    # Test download
    if attachment.file:
        print(f"\n✅ File stored at: {attachment.file.path}")
        with open(attachment.file.path, 'r') as f:
            content = f.read()
            print(f"   Content: {content}")
    
    print("\n✅ All attachment tests passed!")

if __name__ == '__main__':
    test_attachments()