from django.urls import path
from .views import RegisterView, FollowView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="sign_up"),
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),
]