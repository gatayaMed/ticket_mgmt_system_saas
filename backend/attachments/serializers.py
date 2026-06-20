# attachments/serializers.py
from rest_framework import serializers
from .models import Attachment

class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = [
            'id', 'ticket', 'user', 'user_email', 'user_username',
            'file', 'file_url', 'filename', 'file_size', 'file_size_display',
            'content_type', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'filename', 'file_size', 'content_type', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_display(self, obj):
        """Convert file size to human-readable format"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"

class AttachmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attachments - ticket is set in the view"""
    
    class Meta:
        model = Attachment
        fields = ['file', 'description']  # REMOVED 'ticket' from here

    def validate_file(self, value):
        """Validate file size and type"""
        # Max file size: 10MB
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds limit (max {max_size / (1024 * 1024):.0f}MB)"
            )
        return value