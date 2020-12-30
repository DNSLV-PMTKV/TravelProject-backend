from django.db import models
from django.contrib.auth import get_user_model


class ForgotPassword(models.Model):
    """ Model for forgot password. """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Forgot Password Requests'
        db_table = 'forgot_password'
