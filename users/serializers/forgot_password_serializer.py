from rest_framework import serializers
from utils.validators import email_is_correct


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        if not email_is_correct(value):
            raise serializers.ValidationError('Please enter a valid email')
        return value
