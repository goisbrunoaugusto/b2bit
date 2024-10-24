import logging

from .models import Post
from .serializers import PostSerializer, LikeSerializer, EditSerializer, ListPostSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache

def clear_user_cache(user_id):
    for page_number in cache.keys(f"*{user_id}*"):
        cache.delete(page_number)

class CreatePostView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        clear_user_cache(self.request.user.id)
        serializer.save(user=self.request.user)

class DeletePostView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            return Response({"error: You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        clear_user_cache(self.request.user.id)
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
            clear_user_cache(self.request.user.id)
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
            clear_user_cache(self.request.user.id)
            message = "Post unliked successfully."
        else:
            post.like.add(user)
            clear_user_cache(self.request.user.id)
            message = "Post liked successfully."

        return Response({
            "message": message,
            "likes_count": post.like.count()
        }, status=status.HTTP_200_OK)

class PostPagination(PageNumberPagination):
    page_size = 5

@method_decorator(vary_on_headers('Authorization'), name='dispatch')
@method_decorator(cache_page(settings.CACHE_TTL), name='dispatch')
class FollowingPostsView(ListAPIView):
    serializer_class = ListPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination

    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()

        return Post.objects.filter(user__in=following_users).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        user = self.request.user
        page_number = request.query_params.get('page', 1)
        cache_key = f"following_posts_{user.id}_page_{page_number}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
        return Response(serializer.data)

@method_decorator(vary_on_headers('Authorization'), name='dispatch')
@method_decorator(cache_page(settings.CACHE_TTL), name='dispatch')
class UserPostsView(ListAPIView):
    serializer_class = ListPostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        user = self.request.user
        page_number = request.query_params.get('page', 1)
        cache_key = f"my_posts_{user.id}_page_{page_number}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)
        return Response(serializer.data)