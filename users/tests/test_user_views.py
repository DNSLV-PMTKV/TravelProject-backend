from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.test import APIClient


def generate_detail_url(user_id):
    """ Return user detail URL """
    return reverse('users:users_detail_view', args=[user_id])


class UserViewSetTests(TestCase):
    """ Tests for retrieving/updating/deleting users. """

    list_url = reverse('users:users_list')
    me_url = reverse('users:logged_user')

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='first_name',
            last_name='last_name',
            is_active=True)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.other = get_user_model().objects.create_user(
            email='other@test.com',
            password='test123',
            first_name='other_f',
            last_name='other_l',
            is_active=True)

    def test_get_logged_user_info(self):
        """ test getting logged user info """

        res = self.client.get(self.me_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('first_name'), self.user.first_name)
        self.assertEqual(res.data.get('last_name'), self.user.last_name)
        self.assertEqual(res.data.get('email'), self.user.email)

    def test_update_user_info(self):
        """ test updating logged user info. """

        data = {
            'first_name': 'update1',
            'last_name': 'update2',
            'email': 'updated@email.com'
        }

        res = self.client.put(generate_detail_url(self.user.id), data)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(res.data.get('first_name'), 'update1')
        self.assertEqual(res.data.get('last_name'), 'update2')
        self.assertEqual(res.data.get('email'), 'updated@email.com')

    def test_delete_user(self):
        """ test deleting user. """

        user_id = self.user.id
        res = self.client.delete(generate_detail_url(user_id))

        self.assertEqual(status.HTTP_204_NO_CONTENT, res.status_code)

        self.client.get(generate_detail_url(user_id))
        self.assertRaises(expected_exception=NotFound)

    def test_get_other_user_info(self):
        """ test retrieving other user info. """

        res = self.client.get(generate_detail_url(self.other.id))

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(res.data.get('first_name'), self.other.first_name)
        self.assertEqual(res.data.get('last_name'), self.other.last_name)
        self.assertEqual(res.data.get('email'), self.other.email)

    def test_update_other_user_info(self):
        """ test updating other user info. """

        data = {
            'first_name': 'update'
        }

        res = self.client.put(generate_detail_url(self.other.id), data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertEqual('other_f', self.other.first_name)

    def test_delete_other_user(self):
        """ test deleting other user. """

        res = self.client.delete(generate_detail_url(self.other.id))

        self.assertEqual(status.HTTP_403_FORBIDDEN, res.status_code)
        self.assertIsNotNone(self.other)

    def test_get_all_active_users(self):
        """ test retrieving list of all users. """

        res = self.client.get(self.list_url)

        self.assertEqual(status.HTTP_200_OK, res.status_code)
        self.assertEqual(len(res.data), 2)
