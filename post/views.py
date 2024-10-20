from .models import Post
from .serializers import PostSerializer, LikeSerializer, EditSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

class EditPostView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = EditSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
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

    def perform_create(self, serializer):
        post = self.get_object()
        user = self.request.user

        if post.like.filter(id=user.id).exists():
            post.like.remove(user)
        else:
            post.like.add(user)

        post.save()

    def get_object(self):
        pk = self.kwargs.get('pk')
        return Post.objects.get(pk=pk)

    def create(self, request, *args, **kwargs):
        post = self.get_object()
        self.perform_create(None)  # Chama o método perform_create para o toggle
        return Response({'likes_count': post.like.count()})