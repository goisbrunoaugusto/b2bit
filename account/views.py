from rest_framework.views import APIView
from .serializers import UserSerializer, FollowSerializer, FollowingUserSerializer, FollowerUserSerializer
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateDestroyAPIView
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

        return Response(message)

class FollowerListView(RetrieveUpdateDestroyAPIView):
    queryset = UserData.objects.all()
    serializer_class = FollowerUserSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        followers = user.followers.all()
        serializer = self.get_serializer(followers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowingListView(RetrieveUpdateDestroyAPIView):
    queryset = UserData.objects.all()
    serializer_class = FollowingUserSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        following = user.following.all()
        serializer = self.get_serializer(following, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
