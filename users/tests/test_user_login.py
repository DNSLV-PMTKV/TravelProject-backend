from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework import serializers


class LoginAPITests(TestCase):
    """ Tests for user login. """

    url = reverse('users:login')

    def setUp(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@test.test',
            'password': 'test123',
            'is_active': True
        }
        get_user_model().objects.create_user(**user_data)

    def test_authentication_with_valid_data(self):
        """ Test logging with valid data. """
        data = {'email': 'test@test.test', 'password': 'test123'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_authentication_without_password(self):
        """ Test logging without password. """
        data = {'email': 'test@test.test'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authentication_with_wrong_password(self):
        """ Test logging with wrong password. """
        data = {'email': 'test@test.test', 'password': 'wrongPass'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authentication_without_confirmed_email(self):
        """ Test logging without confirmed email. """
        user_data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test123@test.test',
            'password': 'test123',
        }
        get_user_model().objects.create_user(**user_data)

        data = {'email': 'test123@test.test', 'password': 'test123'}
        response = self.client.post(self.url, data)

        self.assertRaises(expected_exception=serializers.ValidationError)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
