from django.test import TestCase
from django.contrib.auth import get_user_model
from uuid import UUID
from .models import PremiumToken

User = get_user_model()

class PremiumTokenModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123",
        )
        self.token = PremiumToken.objects.create(user=self.user)

    def test_premium_token_creation(self):
        self.assertEqual(self.token.user, self.user)
        self.assertIsInstance(self.token.token, UUID)
        self.assertFalse(self.token.is_used)

    def test_premium_token_string_representation(self):
        self.assertEqual(str(self.token), f"PremiumToken for {self.user.email}")

    def test_premium_token_uniqueness(self):
        with self.assertRaises(Exception):
            PremiumToken.objects.create(user=self.user)

    def test_created_at_field(self):
        self.assertIsNotNone(self.token.created_at)

    def test_update_is_used_field(self):
        self.token.is_used = True
        self.token.save()
        self.assertTrue(self.token.is_used)
