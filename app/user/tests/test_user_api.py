from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'phone_number': '123456',
            'email': "test@example.com",
            'password': "test1234",
        }

        # api post request
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user that already exists fails"""

        payload = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'phone_number': '123456',
            'password': "test1234",
            'email': "test@example.com",
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""

        payload = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'phone_number': '123456',
            'password': "te",
            'email': "test@example.com",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    # def test_phone_validation_test(self):
        # """Test that the phone number must be
        # numerical value within 10 characters"""

        # payload = {
        # 'first_name': 'test',
        # 'last_name': 'test',
        # 'username': 'test',
        # 'phone_number': 'cahod',
        # 'password': "te",
        # 'email': "test@example.com",
    # }

        # res = self.client.post(CREATE_USER_URL)
        # self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # phone_number_correct = get_user_model().objects.filter(
        # phone_number=payload['phone_number']).exists()
        # self.assertTrue(phone_number_correct)

    def test_new_authtoken(self):
        """test that a token is used for user"""

        params = {
            'first_name': 'test',
            'last_name': 'test',
            'username': 'test',
            'phone_number': '123456',
            'email': 'test@example.com',
            'password': 'test1111',
        }

        payload = {
            'email': 'test@example.com',
            'password': 'test1111'
        }

        create_user(**params)
        res = self.client.post(TOKEN_URL, payload, format='json')
        print(res.data)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_credential(self):
        """test that token is not created if invalid credentials are given"""
        create_user(first_name='test', last_name='test', username='test',
                    phone_number='1234567', email='test@example.com', password="testtest")
        payload = {
            'email': 'test@example.com',
            'password': 'test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_not_exist_user(self):
        """test that token is not created if user is not exist"""
        payload = {
            'email': 'test@example.com',
            'password': 'test1111'
        }
        user = get_user_model().objects.filter(email=payload['email']).exists()
        res = self.client.post(TOKEN_URL, payload)
        self.assertFalse(user)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(
            TOKEN_URL, {'email': 'test', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_auauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            first_name='test',
            last_name='test',
            username='test',
            phone_number='123456',
            email='test@example.com',
            password='test1234',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'username': self.user.username,
            'phone_number': self.user.phone_number,
            'email': self.user.email,
        })

    def test_me_not_allowed(self):
        """Test that Test me is not allowed on the url"""

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'username': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
