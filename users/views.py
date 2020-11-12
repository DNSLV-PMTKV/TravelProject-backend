import uuid
import datetime
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from .models import UnconfirmedUser, User


def send_confirmation_email(to_mail: str, token: str):

    subject = 'Hello?'
    context = {
        'url': f'/api/confirm?token={token}'
    }
    template = render_to_string('confirm_email.html', context)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(subject, 'Activate your account',
              from_mail, [to_mail], html_message=template)


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

        return Response(self.serializer_class(user).data, status=status.HTTP_201_CREATED)


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

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            token, created = Token.objects.get_or_create(
                user=serializer.validated_data['user'])
            utc_now = datetime.datetime.utcnow()

            if not created and token.created < utc_now - datetime.timedelta(
                    hours=settings.TOKEN_EXPIRE_IN_HOURS):
                token.delete()
                token = Token.objects.create(
                    user=serializer.validated_data['user'])
                token.created = datetime.datetime.utcnow()
                token.save()

            return Response({'token': token.key})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(RetrieveAPIView):
    """ Delete logged user token from the database. """

    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
