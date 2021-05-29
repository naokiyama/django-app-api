from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class UserAdminModelTests(TestCase):

    def setUp(self):

        self.client = Client()

        first_name = 'test'
        last_name = 'test'
        username = 'test'
        phone_number = '123456'
        password = "test1234"
        email = "test@example.com"

        self.admin_user = get_user_model().objects.create_superuser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number,
            email=email,
            password=password
        )

        # ログインされた状態かどうかをテストする(is_authenticatedがtrueかどうか)
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create(
            first_name=first_name,
            last_name=last_name,
            username="test2",
            phone_number=phone_number,
            email="test1234@example.com",
            password=password
        )

    def test_user_listed(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.admin_user.username)
        self.assertContains(res, self.admin_user.email)
