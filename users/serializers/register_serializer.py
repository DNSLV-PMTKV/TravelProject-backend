from django.contrib.auth import get_user_model
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email", "password", "password2"]
        read_only_fields = [
            "id",
        ]

    def validate(self, attrs):
        """Validate password and password2."""

        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            msg = "Passwords are not identical."
            raise serializers.ValidationError(msg)

        attrs.pop("password2", None)

        return attrs
