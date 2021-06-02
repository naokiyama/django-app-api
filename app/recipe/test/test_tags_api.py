from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PubllicTagApiTests(TestCase):
    """Test that publicky available Tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that required for retrieved tag"""

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            first_name='test',
            last_name='test',
            username='test',
            phone_number='123456',
            email='test@example.com',
            password='test1234')
        self.client.force_authenticate(self.user)

    def test_private_login_reuired(self):
        Tag.objects.create(user=self.user, name="Vergan")
        Tag.objects.create(user=self.user, name="Desert")

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_user(self):
        """Test that tag returned is for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            first_name='test2',
            last_name='test2',
            username='test2',
            phone_number='123456',
            email='test2@example.com',
            password='test2222'
        )

        Tag.objects.create(user=user2, name='Meat')
        tag = Tag.objects.create(user=self.user, name='Fruity')
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {"name": ''}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
