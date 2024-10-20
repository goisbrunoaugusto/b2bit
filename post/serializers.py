from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')


    class Meta:
        model = Post
        fields = ['user', 'content', 'id']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = []

class EditSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['user', 'content', 'likes_count']

    def get_likes_count(self, obj):
        return obj.like.count()