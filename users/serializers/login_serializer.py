from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """ Serializer for the user authentication object. """

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """ Validate and authenticate the user. """

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = ('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authentication')

        if user and not user.is_active:
            raise serializers.ValidationError(
                'Please, confirm your email address first.')

        attrs['user'] = user
        return attrs
