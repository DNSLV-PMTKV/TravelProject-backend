from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name',
                  'last_name', 'is_active', 'profile_pic']
        read_only_fields = ['id', 'is_staff',
                            'is_active', 'is_super_user', 'profile_pic']
