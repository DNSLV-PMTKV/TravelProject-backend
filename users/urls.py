from django.urls import path

from .views import (ConfirmEmailView, ForgotPasswordView, LoginView,
                    LogoutView, RegisterView, UserViewSet)

app_name = 'users'

user_details = UserViewSet.as_view(
    {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

users_list = UserViewSet.as_view({'get': 'list'})

logged_user = UserViewSet.as_view({'get': 'get_auth_user'})

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users/<int:id>', user_details, name='users_detail_view'),
    path('users/me', logged_user, name='logged_user'),
    path('users', users_list, name='users_list'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password')
]
