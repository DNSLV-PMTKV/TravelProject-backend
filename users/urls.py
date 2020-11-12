from django.urls import path

from .views import RegisterView, ConfirmEmailView, LoginView, LogoutView

app_name = 'users'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]
