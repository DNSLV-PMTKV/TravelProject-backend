import uuid
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from .models import UnconfirmedUser, User


def send_confirmation_email(to_mail: str, token: str):

    subject = 'Hello?'
    message = 'THIS IS YOUR TOKEN: {}'.format(token)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(subject, message, from_mail, [to_mail])


class RegisterView(CreateAPIView):
    """ Registration view """

    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def _create_token(self):
        return uuid.uuid4()

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = User(**serializer.validated_data)
        unconfirmed_user = UnconfirmedUser(
            user=user, token=self._create_token())

        try:
            send_confirmation_email(user.email, unconfirmed_user.token)
        except:
            raise APIException(
                'Something went wrong. Please try again in a few moments.')

        user.set_password(user.password)
        user.save()
        unconfirmed_user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConfirmEmailView(APIView):

    def get(self, request):
        token = request.query_params.get('token', None)

        if token is None:
            raise APIException('No token was provided.')

        try:
            unconfirmed_user = UnconfirmedUser.objects.get(token=token)
        except UnconfirmedUser.DoesNotExist:
            raise NotFound('You have already actived your account.')

        user = User.objects.get(id=unconfirmed_user.user_id)
        user.is_active = True
        unconfirmed_user.delete()
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):

    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
