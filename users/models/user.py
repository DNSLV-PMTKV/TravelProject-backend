import uuid
import os
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)


def user_image_file_path(_, filename):
    """Generate file path for new user image."""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return filename


class UserManager(BaseUserManager):
    """ Custom user manager """

    def create_user(self, email, password=None, **kwargs):
        """ Creates and saves a regular user """

        if not email:
            raise ValueError('User must have an email address.')
        user: User = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        """ Creates and saves a super user """

        user: User = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model. """

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    profile_pic = models.ImageField(
        null=True, upload_to=user_image_file_path)
    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    @property
    def fullname(self):
        return self.first_name + self.last_name

    def upload_photo(self, picture):
        if self.profile_pic:
            os.remove(self.profile_pic.path)
        self.profile_pic = picture
        self.save()

    def remove_photo(self):
        if self.profile_pic:
            os.remove(self.profile_pic.path)
        self.profile_pic.delete()
        self.save()

    def delete(self, using=None, keep_parents=False):
        if self.profile_pic:
            os.remove(self.profile_pic.path)
        super().delete()

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Users'
        db_table = 'users'

    USERNAME_FIELD = 'email'
