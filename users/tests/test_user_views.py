import os

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIClient
from users.models import User


def generate_detail_url(user_id):
    """Return user detail URL"""
    return reverse("users:users_detail_view", args=[user_id])


class UserViewSetTests(TestCase):
    """Tests for retrieving/updating/deleting users."""

    list_url = reverse("users:users_list")
    me_url = reverse("users:logged_user")
    photo_url = reverse("users:change_photo")
    password_url = reverse("users:change_password")

    def setUp(self):
        self.user: User = get_user_model().objects.create_user(
            email="test@test.com",
            password="test123",
            first_name="first_name",
            last_name="last_name",
            is_active=True,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.other = get_user_model().objects.create_user(
            email="other@test.com",
            password="test123",
            first_name="other_f",
            last_name="other_l",
            is_active=True,
        )

    def tearDown(self):
        if self.user.profile_pic and os.path.isfile(self.user.profile_pic.path):
            self.user.remove_photo()

    def test_get_logged_user_info(self):
        """test getting logged user info"""

        res = self.client.get(self.me_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("first_name"), self.user.first_name)
        self.assertEqual(res.data.get("last_name"), self.user.last_name)
        self.assertEqual(res.data.get("email"), self.user.email)

    def test_update_user_info(self):
        """test updating logged user info."""

        data = {
            "first_name": "update1",
            "last_name": "update2",
            "email": "updated@email.com",
        }

        res = self.client.put(generate_detail_url(self.user.id), data)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(res.data.get("first_name"), "update1")
        self.assertEqual(res.data.get("last_name"), "update2")
        self.assertEqual(res.data.get("email"), "updated@email.com")

    def test_delete_user(self):
        """test deleting user."""

        user_id = self.user.id
        res = self.client.delete(generate_detail_url(user_id))

        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)

        self.client.get(generate_detail_url(user_id))
        self.assertRaises(expected_exception=NotFound)

    def test_get_other_user_info(self):
        """test retrieving other user info."""

        res = self.client.get(generate_detail_url(self.other.id))

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(res.data.get("first_name"), self.other.first_name)
        self.assertEqual(res.data.get("last_name"), self.other.last_name)
        self.assertEqual(res.data.get("email"), self.other.email)

    def test_update_other_user_info(self):
        """test updating other user info."""

        data = {"first_name": "update"}

        res = self.client.put(generate_detail_url(self.other.id), data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertEqual("other_f", self.other.first_name)

    def test_delete_other_user(self):
        """test deleting other user."""

        res = self.client.delete(generate_detail_url(self.other.id))

        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertIsNotNone(self.other)

    def test_get_all_active_users(self):
        """test retrieving list of all users."""

        res = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(len(res.data.get("results")), 2)

    def test_upload_profile_picture(self):
        """test uploading profile picture"""

        image = SimpleUploadedFile(
            "file.png", b"file_content", content_type="image/png"
        )

        res = self.client.put(self.photo_url, {"profile_pic": image})

        self.assertEqual(res.data.get("profile_pic"), self.user.profile_pic.url)
        self.assertTrue(os.path.isfile(self.user.profile_pic.path))

    def test_remove_profile_picture(self):
        """test if profile picture is removed from db/file system"""
        image = SimpleUploadedFile(
            "file.png", b"file_content", content_type="image/png"
        )
        self.client.put(self.photo_url, {"profile_pic": image})

        image_location = self.user.profile_pic.path

        res = self.client.put(self.photo_url, {"profile_pic": ""})

        self.assertIsNone(res.data.get("profile_pic"))
        self.assertFalse(os.path.isfile(image_location))

    def test_delete_user_with_profile_pic(self):
        """test if profile picture is removed from file system upon user delete"""
        image = SimpleUploadedFile(
            "file.png", b"file_content", content_type="image/png"
        )
        self.client.put(self.photo_url, {"profile_pic": image})

        image_location = self.user.profile_pic.path

        res = self.client.delete(generate_detail_url(self.user.id))

        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)
        self.assertFalse(os.path.isfile(image_location))

    def test_update_profile_picture(self):
        """test if user profile picture is updated"""
        image1 = SimpleUploadedFile(
            "file.png", b"file_content", content_type="image/png"
        )
        self.client.put(self.photo_url, {"profile_pic": image1})

        first_image_location = self.user.profile_pic.path

        image2 = SimpleUploadedFile(
            "file.jpeg", b"file_content2", content_type="image/jpeg"
        )
        res = self.client.put(self.photo_url, {"profile_pic": image2})

        second_image_location = self.user.profile_pic.path

        self.assertNotEqual(first_image_location, second_image_location)
        self.assertFalse(os.path.isfile(first_image_location))
        self.assertTrue(os.path.isfile(second_image_location))
        self.assertEqual(res.data.get("profile_pic"), self.user.profile_pic.url)

    def test_update_password(self):
        """test update password endpoint"""
        data = {
            "old_password": "test123",
            "new_password": "new_test",
            "re_password": "new_test",
        }

        current_user_password = self.user.password

        res = self.client.put(self.password_url, data)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.user.password, current_user_password)
        self.assertNotEqual(self.user.password, data.get("new_test"))

    def test_update_password_incorrect_old_password(self):
        """test to verify old password is matching user password"""
        data = {
            "old_password": "test124",
            "new_password": "new_test",
            "re_password": "new_test",
        }

        res = self.client.put(self.password_url, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(expected_exception=ValidationError)

    def test_update_password_new_password_not_matching(self):
        """test if new_password and re_password are matching"""
        data = {
            "old_password": "test123",
            "new_password": "new_tes",
            "re_password": "new_test",
        }

        res = self.client.put(self.password_url, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(expected_exception=ValidationError)
