from django.test import TestCase
from django.core import mail
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status


class RegistrationAPITests(TestCase):
    """Tests for user registration."""

    url = reverse("users:register")

    def test_user_registration_with_dismatcing_password(self):
        """Test creating user with dismatching passwords."""
        user_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "test@test.test",
            "password": "test123",
            "password2": "test",
        }
        response = self.client.post(self.url, user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_without_mail(self):
        """Test creating user without mail."""
        user_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "",
            "password": "test123",
            "password2": "test",
        }
        response = self.client.post(self.url, user_data)

        self.assertRaises(expected_exception=ValueError)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_object_is_created(self):
        """Test saving user data to db."""
        user_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "test@test1234.asd",
            "password": "test123",
            "password2": "test123",
        }
        response = self.client.post(self.url, user_data)

        self.assertTrue(
            get_user_model().objects.filter(id=response.data.get("id")).exists()
        )

    def test_send_user_email(self):
        """Test sending email to the user."""
        user_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "this_is_auto_test@mailinator.com",
            "password": "test123",
            "password2": "test123",
        }
        self.client.post(self.url, user_data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hello?")

    def test_register_same_mail_twice(self):
        """Test trying ot register users with same email."""
        user_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "this_is_auto_test@mailinator.com",
            "password": "test123",
            "password2": "test123",
        }
        response1 = self.client.post(self.url, user_data)
        response2 = self.client.post(self.url, user_data)

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(expected_exception=ValueError)
