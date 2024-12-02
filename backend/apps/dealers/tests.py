from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import CarDealer

User = get_user_model()

class CarDealerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123",
        )
        self.car_dealer = CarDealer.objects.create(
            name="Test Car Dealer",
            user=self.user,
        )

    def test_car_dealer_creation(self):
        self.assertEqual(self.car_dealer.name, "Test Car Dealer")
        self.assertEqual(self.car_dealer.user, self.user)

    def test_car_dealer_string_representation(self):
        self.assertEqual(str(self.car_dealer), "Test Car Dealer")

    def test_car_dealer_with_null_user(self):
        car_dealer_without_user = CarDealer.objects.create(name="Dealer Without User")
        self.assertIsNone(car_dealer_without_user.user)

    def test_car_dealer_user_deletion(self):
        self.user.delete()
        self.car_dealer.refresh_from_db()
        self.assertIsNone(self.car_dealer.user)

    def test_car_dealer_creation_date(self):
        self.assertIsNotNone(self.car_dealer.created_at)
