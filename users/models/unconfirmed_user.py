from django.db import models
from django.contrib.auth import get_user_model


class UnconfirmedUser(models.Model):
    """ Model for unconfirmed users. """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Unconfirmed Users'
        db_table = 'unconfirmed_users'
