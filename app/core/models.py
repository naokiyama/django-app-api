from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
# Create your models here.

# usermodelにはセキュリティを高めるためにuuidの使用を検討する


class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, username,
                    phone_number, email, password):

        if not email:
            raise ValueError('Users must have an email adress')

        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone_number=phone_number,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, username,
                         phone_number, email, password=None):

        user = self.create_user(
            first_name,
            last_name,
            username,
            phone_number=phone_number,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=8)

    # required
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',
                       'username', 'phone_number']

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def full_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    def __str__(self):
        return self.email
