"""
Serializers for the Post model
"""
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the CreatePostView
    """
    user = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Post
        fields = [ 'id', 'user', 'content', 'image', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for the LikeView
    """
    class Meta:
        model = Post
        fields = []

class EditSerializer(serializers.ModelSerializer):
    """
    Serializer for the EditPostView
    """
    likes_count = serializers.SerializerMethodField()
    post_owner = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'content', 'likes_count', 'post_owner']

    def get_likes_count(self, obj):
        """
        Get the number of likes for a post
        """
        return obj.like.count()

    def get_post_owner(self, obj):
        """
        Get the email of the user who created the post
        """
        return obj.user.email

class ListPostSerializer(serializers.ModelSerializer):
    """
    Serializer for the ListPostView
    """
    user = serializers.ReadOnlyField(source='user.email')
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'content', 'id', 'likes_count', 'image','created_at']

    def get_likes_count(self, obj):
        """
        Get the number of likes for a post
        """
        return obj.like.count()
