from .views import CreatePostView, DeletePostView, EditPostView, LikePostView, FollowingPostsView, UserPostsView
from django.urls import path


urlpatterns = [
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('delete/<int:pk>/', DeletePostView.as_view(), name='delete_post'),
    path('edit/<int:pk>/', EditPostView.as_view(), name='edit_post'),
    path('like/<int:pk>/', LikePostView.as_view(), name='like_post'),
    path('feed/', FollowingPostsView.as_view(), name='feed'),
    path('feed/current/', UserPostsView.as_view(), name='user_posts'),
]
