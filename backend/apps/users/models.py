from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    ROLES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('manager', 'Manager'),
        ('administrator', 'Administrator')
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='buyer')
    is_premium = models.BooleanField(default=False)
    premium_expiry = models.DateField(null=True, blank=True)

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("can_view_statistics", "Can view statistics"),
            ("can_manage_users", "Can manage users"),
            ("can_manage_cars", "Can manage cars"),
        ]
