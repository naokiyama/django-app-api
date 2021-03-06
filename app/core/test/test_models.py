from django.test import TestCase
from django.contrib.auth import get_user_model
from .. import models
from core import models
# Create your tests here.


def sample_user(
        first_name='test',
        last_name='test',
        username='test',
        phone_number='123456',
        email="test@example.com",
        password="test1234"):
    # crete sample user
    return get_user_model().objects.create_user(
        first_name, last_name,
        username, phone_number,
        email, password)


class UserModel(TestCase):

    def test_create_user_with_confirm(self):
        "test: confirmation of creating user"
        first_name = 'test'
        last_name = 'test'
        username = 'test'
        phone_number = '123456'
        password = "test1234"
        email = "test@example.com"

        user = get_user_model().objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number,
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_with_confirm(self):
        "test: confirmation of creating superuser"
        first_name = 'test'
        last_name = 'test'
        username = 'test'
        phone_number = '123456'
        password = "test1234"
        email = "test@example.com"

        user = get_user_model().objects.create_superuser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number,
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test: confirmation of email normalization"""
        first_name = 'test'
        last_name = 'test'
        username = 'test'
        phone_number = '123456'
        password = "test1234"
        email = "test@example.com"

        user = get_user_model().objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number,
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test: creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                first_name='test',
                last_name='test',
                username='test',
                phone_number='123456',
                password="test1234",
                email=None
            )

    def test_new_user_invalid_username(self):
        """test: creating user with no username
         raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                first_name='test',
                last_name='test',
                username=None,
                phone_number='123456',
                password="test1234",
                email='1234@example.com'
            )

    def test_create_new_tag(self):

        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vergan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_create_new_ingredient(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='apple'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_create_new_recipe(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
    
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myiamge.jpg')
        
        exp_path = f'uploads/recipe/{uuid}.jpg'
