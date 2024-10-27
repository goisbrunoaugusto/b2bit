"""
Serializers for the account app
"""
from rest_framework import serializers
from .models import UserData

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the registration view
    """

    class Meta:
        model = UserData
        fields = ["id", "email", "name", "password"]

    def create(self, validated_data):
        user = UserData.objects.create(email=validated_data['email'],
                                       name=validated_data['name']
                                         )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserInfoView
    """
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = UserData
        fields = ['id', 'email', 'name', 'date_joined', 'following', 'followers']

    def get_following(self, obj):
        """
        Get the number of users the user is following
        """
        return obj.following.count()

    def get_followers(self, obj):
        """
        Get the number of users following the user
        """
        return obj.followers.count()


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for the FollowView
    """

    class Meta:
        model = UserData
        fields = []


class FollowerUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the FollowerListView
    """

    class Meta:
        model = UserData
        fields = ['id', 'name', 'email']

class FollowingUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the FollowingListView
    """

    class Meta:
        model = UserData
        fields = ['id', 'name', 'email']
