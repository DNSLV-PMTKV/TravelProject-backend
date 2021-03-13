from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id', 'is_staff', 'is_active', 'is_super_user']

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it."""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
