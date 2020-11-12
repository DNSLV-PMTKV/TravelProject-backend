from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class LogoutAPITests(TestCase):
    """ Tests for user logout. """

    url = reverse('users:logout')

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='first_name',
            last_name='last_name')

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        Token.objects.create(user=self.user)

    def test_revoking_token(self):
        """ Test logging out. """

        response = self.client.get(self.url)
        tokens = Token.objects.all()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(tokens), 0)

    def test_logging_out_when_not_logged_in(self):
        """ Test logging out when not logged in. """

        self.client.logout()
        Token.objects.filter(user=self.user).delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
