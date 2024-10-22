from .models import Post
from .serializers import PostSerializer, LikeSerializer, EditSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class CreatePostView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DeletePostView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            return Response({"error: You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()

class EditPostView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = EditSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = ['PUT']

    def dispatch(self, request, *args, **kwargs):
        if request.method != 'PUT':
            return Response({"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().dispatch(request, *args, **kwargs)

    def put(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.user.id != request.user.id:
            return Response({"error": "You do not have permission to edit this post."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikePostView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user

        if post.like.filter(id=user.id).exists():
            post.like.remove(user)
            message = "Post unliked successfully."
        else:
            post.like.add(user)
            message = "Post liked successfully."

        return Response({
            "message": message,
            "likes_count": post.like.count()
        }, status=status.HTTP_200_OK)

class PostPagination(PageNumberPagination):
    page_size = 5

class FollowingPostsView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination

    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()

        return Post.objects.filter(user__in=following_users).order_by('-created_at')

