from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test the oublic user api """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """ test user creation """
        payload = {
            'email': 'test@a.com',
            'password': 'testpassword',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        payload = {
            'email': 'medo@ff.com',
            'password': 'my pass',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ test that pass should be tall enough """
        payload = {
            'email': 'test@aa.com',
            'password': 'ass',
            'name': 'medo'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(
            email=payload['email']).exists()

        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test user-token creation"""
        payload = {'email': 'test@7a7a.com', 'password': 'myfuckenpassword'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials"""
        create_user(email='q@g.com', password='xcvfgjmfgh')
        payload = {'email': 'q@g.com', 'password': 'wrong-asshole'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_taken_no_user(self):
        """Test token not creted if user doesn't exist"""
        payload = {'email': 'test@ggg.com', 'password': 'test-mypass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and pass are required"""
        res = self.client.post(
            TOKEN_URL, {'email': 'aj@j.cm', 'password': 'd'})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
