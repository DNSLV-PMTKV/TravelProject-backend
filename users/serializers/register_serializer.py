from django.contrib.auth import get_user_model
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name',
                  'email', 'password', 'password2']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {
                    'input_type': 'password'
                }
            }
        }
        read_only_fields = ['id', ]

    def validate(self, attrs):
        """Validate password and password2."""

        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            msg = ('Passwords are not identical.')
            raise serializers.ValidationError(msg)

        attrs.pop('password2', None)

        return attrs
