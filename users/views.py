import datetime
import uuid

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .models import ForgotPassword, UnconfirmedUser, User
from .permissions import UserPermissions
from .serializers import (ForgotPasswordSerializer, LoginSerializer,
                          RegisterSerializer, UpdatePasswordSerializer,
                          UserSerializer)


def send_confirmation_email(to_mail: str, token: str):

    subject = 'Hello?'
    context = {
        'url': f'/api/confirm?token={token}'
    }
    template = render_to_string('confirm_email.html', context)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(subject, 'Activate your account',
              from_mail, [to_mail], html_message=template)


def send_reset_password_email(to_mail: str, reset_token: str):
    subject = 'Reset your password'
    context = {
        'url': f'/api/confirm_reset_password?token={reset_token}'
    }
    template = render_to_string('reset_password_email.html', context)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(subject, 'You\'ve requested a password change.',
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
            utc_now = timezone.now()

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


class UserDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [UserPermissions, ]
    serializer_class = UserSerializer
    lookup_field = 'id'
    queryset = get_user_model().objects.filter(is_active=True)


class UserListView(ListAPIView):
    permission_classes = [UserPermissions, ]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.filter(is_active=True)


class ForgotPasswordView(RetrieveAPIView, CreateAPIView, UpdateAPIView):

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdatePasswordSerializer
        return ForgotPasswordSerializer

    def _create_reset_password_token(self, email: str) -> str:
        return urlsafe_base64_encode(bytes(email, 'utf-8'))

    def create(self, request, *args, **kwargs):
        ''' Creates a ForgotPassword entry in the database and sends email to user '''

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        user = get_user_model().objects.get(email=email)

        response = Response(
            {"detail": "Please check your email address."}, status=status.HTTP_200_OK)

        if not user:
            return response

        reset_token = self._create_reset_password_token(email)
        forgot_password = ForgotPassword(user=user, token=reset_token)

        try:
            send_reset_password_email(email, reset_token)
        except:
            raise APIException(
                'Something went wrong. Please try again in a few moments.')

        forgot_password.save()

        return response

    def retrieve(self, request, *args, **kwargs):
        ''' Validate if the reset token is correct '''

        reset_token = request.query_params.get('reset_token', None)

        try:
            forgot_password = ForgotPassword.objects.get(token=reset_token)
        except ForgotPassword.DoesNotExist:
            raise NotFound('Token is invalid.')

        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)
        if forgot_password.created_at < utc_now - datetime.timedelta(
                hours=settings.TOKEN_EXPIRE_IN_HOURS):
            forgot_password.delete()
            raise ValidationError('Token has expired')

        return Response(None, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        ''' Update users password '''

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get('reset_token')

        forgot_password = ForgotPassword.objects.get(token=token)
        user = forgot_password.user

        user.set_password(serializer.validated_data.get('password'))
        user.save()
        forgot_password.delete()

        return Response(None, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        pass
