from collections import OrderedDict

from rest_framework import serializers

from users.models import User


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    new_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    re_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password", "re_password")

    def validate(self, attrs: OrderedDict):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        re_password = attrs.get("re_password")

        user: User = self.context["request"].user

        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is not valid.")

        if new_password != re_password:
            raise serializers.ValidationError(
                "New password and Re-password are not matching."
            )

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()

        return instance
