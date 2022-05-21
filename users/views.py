import datetime
import logging

import pytz
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from .models import ForgotPassword, UnconfirmedUser, User
from .permissions import UserPermissions
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    UserProfilePictureSerializer,
    ChangePasswordSerializer,
)

logger = logging.getLogger(__name__)


def send_confirmation_email(to_mail: str, token: str):

    subject = "Hello?"
    context = {"url": f"/api/confirm?token={token}"}
    template = render_to_string("confirm_email.html", context)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(
        subject, "Activate your account", from_mail, [to_mail], html_message=template
    )


def send_reset_password_email(to_mail: str, reset_token: str):
    subject = "Reset your password"
    context = {"url": f"/api/confirm_reset_password?token={reset_token}"}
    template = render_to_string("reset_password_email.html", context)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(
        subject,
        "You've requested a password change.",
        from_mail,
        [to_mail],
        html_message=template,
    )


def create_base64_token(content: str) -> str:
    return urlsafe_base64_encode(bytes(content, "utf-8"))


class RegisterView(CreateAPIView):
    """Registration view"""

    http_method_names = ["post"]
    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    def create(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = User(**serializer.validated_data)
        unconfirmed_user = UnconfirmedUser(
            user=user, token=create_base64_token(user.email)
        )

        try:
            send_confirmation_email(user.email, unconfirmed_user.token)
        except Exception as exception:
            logger.error(exception)
            raise APIException(
                "Something went wrong. Please try again in a few moments."
            )

        user.set_password(user.password)
        user.save()
        unconfirmed_user.save()

        return Response(
            self.serializer_class(user).data, status=status.HTTP_201_CREATED
        )


class ConfirmEmailView(APIView):

    http_method_names = ["get"]

    def get(self, request: Request):
        token = request.query_params.get("token", None)

        if token is None:
            raise APIException("No token was provided.")

        try:
            unconfirmed_user = UnconfirmedUser.objects.get(token=token)
        except UnconfirmedUser.DoesNotExist:
            raise NotFound("You have already actived your account.")

        user = User.objects.get(id=unconfirmed_user.user_id)
        user.is_active = True
        unconfirmed_user.delete()
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):

    http_method_names = ["post"]
    serializer_class = LoginSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request: Request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if not user:
            raise ValidationError(
                "Unable to authenticate with provided credentials.",
                code="authentication",
            )

        if user and not user.is_active:
            raise ValidationError("Please, confirm your email address first.")

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.id, "user_email": user.email}
        )


class LogoutView(RetrieveAPIView):
    """Delete logged user token from the database."""

    http_method_names = ["get"]
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class UserViewSet(ModelViewSet):
    http_method_names = ["get", "put", "delete", "head"]
    queryset = get_user_model().objects.filter(is_active=True)
    serializer_class = UserSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated, UserPermissions]

    def get_serializer_class(self):
        if self.action == "change_profile_picture":
            return UserProfilePictureSerializer
        return UserSerializer

    @action(methods=["get"], detail=True)
    def get_auth_user(self, request: Request):
        serializer = self.get_serializer_class()
        data = serializer(request.user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=["put"], detail=True)
    def change_profile_picture(self, request: Request):
        serializer = self.get_serializer_class()
        data = serializer(request.data).instance
        user: User = request.user
        if data.get("profile_pic"):
            user.upload_photo(data.get("profile_pic"))
        else:
            user.remove_photo()
        return_data = UserSerializer(user)
        return Response(return_data.data, status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    http_method_names = ["put", "head"]
    queryset = get_user_model().objects.filter(is_active=True)
    permission_classes = [IsAuthenticated, UserPermissions]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj


class ForgotPasswordView(RetrieveAPIView, CreateAPIView, UpdateAPIView):

    http_method_names = ["post", "put", "get", "head"]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ResetPasswordSerializer
        return ForgotPasswordSerializer

    def create(self, request: Request, *args, **kwargs):
        """Creates a ForgotPassword entry in the database and sends email to user"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        response = Response(
            {"detail": "Please check your email address."}, status=status.HTTP_200_OK
        )

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            logger.warning("User tried to send reset password email to: %s", email)
            return response

        reset_token = create_base64_token(f"{email}_reset_token")
        forgot_password = ForgotPassword(user=user, token=reset_token)

        try:
            existing_token = ForgotPassword.objects.get(token=reset_token)
            existing_token.delete()
            logger.info('User "%s" used forgot password api more than once.', email)
        except ForgotPassword.DoesNotExist:
            pass

        try:
            send_reset_password_email(email, reset_token)
        except:
            raise APIException(
                "Something went wrong. Please try again in a few moments."
            )

        forgot_password.save()

        return response

    def retrieve(self, request: Request, *args, **kwargs):
        """Validate if the reset token is correct"""

        reset_token = request.query_params.get("reset_token", None)

        try:
            forgot_password = ForgotPassword.objects.get(token=reset_token)
        except ForgotPassword.DoesNotExist:
            raise NotFound("Token is invalid.")

        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)
        if forgot_password.created_at < utc_now - datetime.timedelta(
            hours=settings.RESET_PASSWORD_TOKEN_EXPIRE_IN_HOURS
        ):
            forgot_password.delete()
            raise ValidationError("Token has expired")

        return Response(None, status=status.HTTP_200_OK)

    def update(self, request: Request, *args, **kwargs):
        """Update users password"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get("reset_token")

        forgot_password = ForgotPassword.objects.get(token=token)
        user = forgot_password.user

        user.set_password(serializer.validated_data.get("password"))
        user.save()
        forgot_password.delete()

        return Response(None, status=status.HTTP_200_OK)
