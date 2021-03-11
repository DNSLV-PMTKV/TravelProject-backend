from django.urls import path

from .views import (ConfirmEmailView, ForgotPasswordView, LoginView,
                    LogoutView, RegisterView, UserDetailView, UserListView, LoggedUserView)

app_name = 'users'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('users/<int:id>', UserDetailView.as_view(), name='users_detail_view'),
    path('users/me', LoggedUserView.as_view(), name='logged_user'),
    path('users', UserListView.as_view(), name='users_list'),
    path('forgot_password', ForgotPasswordView.as_view(), name='forgot_password')
]
