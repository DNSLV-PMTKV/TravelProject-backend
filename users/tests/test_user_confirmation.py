from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound

from users.models import UnconfirmedUser


def generate_token_url(token: str) -> str:
    """Return url with token."""
    return reverse('users:confirm') + f'?token={token}'


class RegistrationAPITests(TestCase):

    confirm_url = reverse('users:confirm')

    def setUp(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test3@test.test',
            'password': 'test123',
            'password2': 'test123',
        }
        self.user = self.client.post(reverse('users:register'), user_data)

    def test_no_token(self):
        self.client.get(self.confirm_url)

        self.assertRaises(APIException)

    def test_correct_token(self):
        unconfirmed_user = UnconfirmedUser.objects.get(
            user=self.user.data.get('id'))

        response = self.client.get(generate_token_url(unconfirmed_user.token))

        user = get_user_model().objects.get(id=self.user.data.get('id'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_active)

    def test_wrong_incorrect_token(self):
        self.client.get(generate_token_url('asd-asd-asd-asd'))

        user = get_user_model().objects.get(id=self.user.data.get('id'))

        self.assertRaises(NotFound)
        self.assertFalse(user.is_active)
