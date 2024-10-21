from rest_framework.views import APIView
from .serializers import UserSerializer, FollowSerializer
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .models import UserData
from rest_framework.permissions import IsAuthenticated, AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class FollowView(CreateAPIView):
    queryset = UserData.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_to_follow = self.get_object()
        current_user = self.request.user

        if user_to_follow.followers.filter(id=current_user.id).exists():
            user_to_follow.followers.remove(current_user)
        else:
            user_to_follow.followers.add(current_user)

        user_to_follow.save()
        serialized_user = self.serializer_class(user_to_follow, context=self.get_serializer_context())
        return Response(FollowSerializer(user_to_follow).data)
