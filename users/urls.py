from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (ConfirmEmailView, ForgotPasswordView, LoginView,
                    RegisterView, UserViewSet, ChangePasswordView)

app_name = 'users'

user_details = UserViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})
users_list = UserViewSet.as_view({'get': 'list'})
logged_user = UserViewSet.as_view({'get': 'get_auth_user'})
change_profile_picture = UserViewSet.as_view({'put': 'change_profile_picture'})

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('<int:id>', user_details, name='users_detail_view'),
    path('me', logged_user, name='logged_user'),
    path('change_photo', change_profile_picture, name='change_photo'),
    path('', users_list, name='users_list'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('change_password', ChangePasswordView.as_view(), name='change_password')
]
