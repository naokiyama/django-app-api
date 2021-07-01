from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')

class PrivateRecipeApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            first_name='test',
            last_name='test',
            username='test',
            phone_number='123456',
            email='test@example.com',
            password='test1234'
        )
        self.client.force_authenticate(self.user)

    

    def test_private_login_required(self):
        Recipe.objects.create(
            user=self.user, title='Steak and mushroo sauce',
            time_minutes=5, price=5.01)
        Recipe.objects.create(
            user=self.user, title='Tomate Soupe',
            time_minutes=4, price=4.01)

        recipes = Recipe.objects.all().order_by('-title')
        # many=True
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retirieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            first_name='test2',
            last_name='test2',
            username='test2',
            phone_number='1234562',
            email='test2@example.com',
            password='test12345'
        )

        recipes = Recipe.objects.create(
            user=self.user, title='Steak and mushroo sauce',
            time_minutes=5, price=5.01)
        serializer = RecipeSerializer(recipes, many=True)
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipes.title)


class PublicRecipeApiTests(TestCase):
    """Test unauthentivated recipe API access"""

    def setUp(self):
        self.Client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
