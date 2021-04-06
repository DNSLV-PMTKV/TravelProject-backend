from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.serializers import UserSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """ Serializer for the user authentication object. """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        user_data = UserSerializer(user).data
        for key, value in user_data.items():
            if key != 'id':
                token[key] = value
        return token
