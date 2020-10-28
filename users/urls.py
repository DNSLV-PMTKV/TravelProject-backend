from django.urls import path

from .views import RegisterView, ConfirmEmailView

app_name = 'users'

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('confirm', ConfirmEmailView.as_view(), name='confirm')
]
