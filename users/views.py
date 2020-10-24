from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.generics import CreateAPIView

from .serializers import RegisterSerializer
from .models import UnconfirmedUser, User


def send_confirmation_email(to_mail: str, token: str):

    subject = 'Alo?'
    message = 'THIS IS YOUR TOKEN: {}'.format(token)
    from_mail = settings.EMAIL_HOST_USER

    send_mail(subject, message, from_mail, [to_mail])


class RegisterView(CreateAPIView):
    """ Registration view """

    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()

    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     unconfirmed_user = UnconfirmedUser.objects.get(
    #         user=response.data.get('id'))
    #     send_confirmation_email(response.data.get(
    #         'email'), unconfirmed_user.token)
    #     return response
