import datetime

import mock
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import serializers, status
from users.models import ForgotPassword


class ForgotPasswordAPITests(TestCase):
    """ Tests for forgotten passwords """

    url = reverse('users:forgot_password')

    def setUp(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@test.test',
            'password': 'test123',
            'is_active': True
        }
        self.user = get_user_model().objects.create_user(**user_data)

    def test_send_forgot_password_email(self):
        """ Test if emails are sending correctly. """

        data = {
            'email': 'test@test.test'
        }

        res = self.client.post(self.url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_not_sending_email(self):
        """ Test if emails are not sent if user does not exists. """

        data = {
            'email': 'asd@zxc.asd'
        }

        res = self.client.post(self.url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_token_creation(self):
        """ Test if token is correctly saved. """

        data = {
            'email': 'test@test.test'
        }

        self.client.post(self.url, data)

        token = ForgotPassword.objects.get(user__email=data['email'])

        self.assertIsNotNone(token)

    def test_user_sends_request_more_than_once(self):
        """ Test if token is being replaced if user sends request more than once. """

        data = {
            'email': 'test@test.test'
        }

        self.client.post(self.url, data)

        ForgotPassword.objects.get(user__email=data['email'])
        self.client.post(self.url, data)

        count = ForgotPassword.objects.filter(
            user__email=data['email']).count()

        self.assertEqual(count, 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_validate_correct_token(self):
        """ Validate correct reset token. """

        data = {
            'email': 'test@test.test'
        }

        self.client.post(self.url, data)

        token = ForgotPassword.objects.get(user__email=data['email']).token

        res = self.client.get(f'{self.url}?reset_token={token}')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_validate_incorrect_token(self):
        """ Validate incorrect reset token. """

        res = self.client.get(f'{self.url}?reset_token=asd')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_validate_expired_token(self):
        """ Validate expired reset token. """

        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = yesterday
            forgot_password = ForgotPassword(
                user=self.user, token='zzz')
            forgot_password.save()

        token = forgot_password.token

        res = self.client.get(f'{self.url}?reset_token={token}')

        self.assertRaises(expected_exception=serializers.ValidationError)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_password(self):
        """ Update user password correctly. """

        data = {
            'email': 'test@test.test'
        }

        self.client.post(self.url, data)
        token = ForgotPassword.objects.get(user__email=data['email']).token

        update_data = {
            'reset_token': token,
            'password': 'aloda',
            'password2': 'aloda'
        }

        res = self.client.put(self.url, update_data,
                              content_type='application/json')

        old_password = self.user.password
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.user.password, old_password)

    def test_update_user_password_missmatch_passwords(self):
        """ Test updating user passwords if not matching. """

        data = {
            'email': 'test@test.test'
        }

        self.client.post(self.url, data)
        token = ForgotPassword.objects.get(user__email=data['email']).token

        update_data = {
            'reset_token': token,
            'password': 'aloda1',
            'password2': 'aloda'
        }

        res = self.client.put(self.url, update_data,
                              content_type='application/json')

        old_password = self.user.password
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(expected_exception=serializers.ValidationError)
        self.assertEqual(self.user.password, old_password)

    def test_send_patch_request(self):
        """ Test sending patch request. """

        data = {'email': 'test@test.test'}

        res = self.client.patch(
            self.url, data, content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
