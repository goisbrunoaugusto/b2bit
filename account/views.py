"""
Views for the account app
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from .models import UserData
from .serializers import UserSerializer, FollowSerializer, FollowingUserSerializer, FollowerUserSerializer, \
    UserInfoSerializer
from .tasks import send_follow_notification_email

class RegisterView(CreateAPIView):
    """
    View for registering a new user
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserInfoView(RetrieveUpdateDestroyAPIView):
    """
    View for getting, updating and deleting user information
    """
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FollowView(RetrieveUpdateDestroyAPIView):
    """
    View for following and unfollowing a user
    """
    queryset = UserData.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_to_follow = self.get_object()
        request_user = request.user

        if user_to_follow.followers.filter(id=request_user.id).exists():
            user_to_follow.followers.remove(request_user)
            request_user.following.remove(user_to_follow)
            message = "Unfollowed"
        else:
            user_to_follow.followers.add(request_user)
            request_user.following.add(user_to_follow)
            message = "Followed"
            send_follow_notification_email.delay(request_user.email, user_to_follow.email)

        return Response(message)


class FollowerListView(ListAPIView):
    """
    View for listing all followers of the authenticated user
    """
    serializer_class = FollowerUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.followers.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_followers = queryset.count()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "total_followers": total_followers,
            "followers": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


class FollowingListView(ListAPIView):
    """
    View for listing all users the authenticated user is following
    """
    serializer_class = FollowingUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.following.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_following = queryset.count()
        serializer = self.get_serializer(queryset, many=True)

        response_data = {
            "total_following": total_following,
            "following": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
