from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from .serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    """ Registration view """

    serializer_class = RegisterSerializer
    queryset = get_user_model().objects.all()
