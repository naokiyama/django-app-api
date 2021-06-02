from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test that publicky not available ingredient api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that required for retreive ingredient"""

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test that private available ingredient api"""

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
        Ingredient.objects.create(user=self.user, name="tomate")
        Ingredient.objects.create(user=self.user, name="apple")
        ingredients = Ingredient.objects.all().order_by('-name')
        # many=Trueはlistに変換
        serializer = IngredientSerializer(ingredients, many=True)
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_gredient_limited_user(self):
        user2 = get_user_model().objects.create_user(
            first_name='test2',
            last_name='test2',
            username='test2',
            phone_number='123456',
            email='test2@example.com',
            password='test2222'
        )
        Ingredient.objects.create(user=user2, name="tomate")
        ingredient = Ingredient.objects.create(user=self.user, name="apple")
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        payload = {
            'name': 'demo'
        }
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test that create invalid ingredient"""

        payload = {
            'name': ""
        }
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
