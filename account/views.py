from rest_framework.views import APIView

from .tasks import send_follow_notification_email
from .serializers import UserSerializer, FollowSerializer, FollowingUserSerializer, FollowerUserSerializer
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from .models import UserData
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class FollowView(RetrieveUpdateDestroyAPIView):
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
