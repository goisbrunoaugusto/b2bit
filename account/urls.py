from django.urls import path
from .views import RegisterView, FollowView, FollowingListView, FollowerListView, UserInfoView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="sign_up"),
    path('follow/<int:pk>/', FollowView.as_view(), name='follow'),
    path('followers/', FollowerListView.as_view(), name='followers'),
    path('following/', FollowingListView.as_view(), name='following_list'),
    path('user/', UserInfoView.as_view(), name='info'),

]