import os
from django.db import models
from django.conf import settings
from tickets.models import Ticket

def attachment_upload_path(instance, filename):
    """Generate upload path for attachments."""
    # Sanitize filename
    import uuid
    ext = filename.split('.')[-1] if '.' in filename else ''
    filename = f"{uuid.uuid4().hex}.{ext}" if ext else f"{uuid.uuid4().hex}"
    return f'tickets/{instance.ticket.ticket_id}/attachments/{filename}'

class Attachment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to=attachment_upload_path, max_length=500)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attachments'
        ordering = ['-created_at']
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
    
    def __str__(self):
        return f"{self.filename} ({self.ticket.ticket_id})"
    
    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = os.path.basename(self.file.name)
            if hasattr(self.file, 'size') and self.file.size:
                self.file_size = self.file.size
            if hasattr(self.file, 'content_type') and self.file.content_type:
                self.content_type = self.file.content_type
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the file from storage when the record is deleted
        if self.file:
            try:
                self.file.delete(save=False)
            except:
                pass
        super().delete(*args, **kwargs)