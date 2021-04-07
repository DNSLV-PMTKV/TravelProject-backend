from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (ConfirmEmailView, ForgotPasswordView, LoginView,
                    LogoutView, RegisterView, UserViewSet)

app_name = 'users'

user_details = UserViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

users_list = UserViewSet.as_view({'get': 'list'})

logged_user = UserViewSet.as_view({'get': 'get_auth_user'})
upload_profile_picture = UserViewSet.as_view({'put': 'upload_profile_pic'})
remove_profile_picture = UserViewSet.as_view({'put': 'remove_profile_pic'})

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users/<int:id>', user_details, name='users_detail_view'),
    path('users/me', logged_user, name='logged_user'),
    path('users/upload_photo', upload_profile_picture, name='upload_photo'),
    path('users/remove_photo', remove_profile_picture, name='remove_photo'),
    path('users', users_list, name='users_list'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password')
]
