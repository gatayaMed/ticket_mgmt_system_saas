from rest_framework import serializers
from .models import Comment
from accounts.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'ticket', 'user', 'user_details',
            'content', 'is_edited', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_edited', 'created_at', 'updated_at']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']