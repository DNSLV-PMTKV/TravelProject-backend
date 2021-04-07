from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserProfilePictureSerializer(serializers.ModelSerializer):
    """Serializer for user object."""

    class Meta:
        model = get_user_model()
        fields = ['profile_pic']
        read_only_fields = ['profile_pic']
