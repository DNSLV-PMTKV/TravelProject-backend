from django.urls import path, re_path

from .views import RegisterView, ConfirmEmailView, LoginView

app_name = 'users'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    re_path('confirm/(?P<token>[0-9]+)$',
            ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login')
]
