from rest_framework import serializers
from .models import UserData
import logging

class UserSerializer(serializers.ModelSerializer):

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

class FollowSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()

    class Meta:
        model = UserData
        fields = ['follower_count']

    def get_follower_count(self, obj):
        logging.debug(f'###################################################{obj}')
        return obj.followers.count()
