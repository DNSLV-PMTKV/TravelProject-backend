from collections import OrderedDict

from rest_framework import serializers


class ResetPasswordSerializer(serializers.Serializer):
    reset_token = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    def validate(self, attrs: OrderedDict):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            msg = "Passwords are not identical."
            raise serializers.ValidationError(msg)

        return attrs
