from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from datetime import date, timedelta

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "role": "buyer",
        }
        self.superuser_data = {
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "securepassword123",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.username, self.user_data["username"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.role, "buyer")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(**self.superuser_data)
        self.assertEqual(superuser.email, self.superuser_data["email"])
        self.assertEqual(superuser.username, self.superuser_data["username"])
        self.assertTrue(superuser.check_password(self.superuser_data["password"]))
        self.assertEqual(superuser.role, "buyer")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_email_uniqueness(self):
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_user_default_role(self):
        user = User.objects.create_user(
            email="newuser@example.com", username="newuser", password="securepassword123"
        )
        self.assertEqual(user.role, "buyer")

    def test_user_role_choices(self):
        with self.assertRaises(ValueError):
            user = User.objects.create_user(
                email="invalidrole@example.com",
                username="invalidrole",
                password="securepassword123",
                role="invalid",
            )

    def test_premium_user_fields(self):
        premium_expiry_date = date.today() + timedelta(days=30)
        user = User.objects.create_user(
            email="premiumuser@example.com",
            username="premiumuser",
            password="securepassword123",
            is_premium=True,
            premium_expiry=premium_expiry_date,
        )
        self.assertTrue(user.is_premium)
        self.assertEqual(user.premium_expiry, premium_expiry_date)

    def test_user_string_representation(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["username"])

    def test_custom_permissions(self):
        permissions = [perm[0] for perm in User._meta.permissions]
        expected_permissions = [
            "can_view_statistics",
            "can_manage_users",
            "can_manage_cars",
        ]
        for perm in expected_permissions:
            self.assertIn(perm, permissions)
