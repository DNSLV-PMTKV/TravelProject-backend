from rest_framework import serializers
from rest_framework.serializers import Serializer


class LoginSerializer(Serializer):
    """Serializer for the user authentication object."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )
