from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
import decimal


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)
    
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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = Recipe.objects.create(
            user=self.user, title='Steak and mushroo sauce',
            time_minutes=5, price=5.01)

        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data['id'], serializer.data['id'])

    def test_create_recipe(self):
         """Test Creating recipe"""
         payload = {
             'title': 'Chocolate cake',
             'time_minutes': 30,
             'price': 5.01,
         }
         res = self.client.post(RECIPE_URL, payload)

         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
         recipe = Recipe.objects.get(id=res.data['id'])
         for key in payload.keys():
             if key == 'title':
                 self.assertEqual(payload[key], getattr(recipe, key))
                
    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user, name='dessert')

        payload = {
             'title': 'Chocolate cake',
             'time_minutes': 30,
             'price': 5.00,
             'tags': [tag1.id, tag2.id],
         }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name='sugger')
        ingredient2 = sample_ingredient(user=self.user, name="win")

        payload = {
             'title': 'Chocolate cake',
             'time_minutes': 30,
             'price': 5.00,
             'ingredients': [ingredient1.id, ingredient2.id],
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

class PublicRecipeApiTests(TestCase):
    """Test unauthentivated recipe API access"""

    def setUp(self):
        self.Client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
       
