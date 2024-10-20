from .views import CreatePostView, DeletePostView, EditPostView, LikePostView
from django.urls import path


urlpatterns = [
    path('create/', CreatePostView.as_view(), name='create_post'),
    path('delete/<int:post_id>/', DeletePostView.as_view(), name='delete_post'),
    path('edit/<int:pk>/', EditPostView.as_view(), name='edit_post'),
    path('like/<int:pk>/', LikePostView.as_view(), name='like_post'),
]
