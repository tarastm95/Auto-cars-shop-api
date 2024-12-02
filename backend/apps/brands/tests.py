from django.test import TestCase
from apps.users.models import User
from apps.brands.models import CarBrand, CarModel, CarBrandReport

class CarBrandModelTest(TestCase):
    def setUp(self):
        self.brand = CarBrand.objects.create(name="Toyota")

    def test_car_brand_creation(self):
        self.assertEqual(self.brand.name, "Toyota")
        self.assertEqual(str(self.brand), "Toyota")

    def test_unique_brand_name(self):
        with self.assertRaises(Exception):
            CarBrand.objects.create(name="Toyota")


class CarModelModelTest(TestCase):
    def setUp(self):
        self.brand = CarBrand.objects.create(name="BMW")
        self.car_model = CarModel.objects.create(brand=self.brand, name="X5")

    def test_car_model_creation(self):
        self.assertEqual(self.car_model.brand.name, "BMW")
        self.assertEqual(self.car_model.name, "X5")
        self.assertEqual(str(self.car_model), "BMW X5")

    def test_car_model_related_to_brand(self):
        self.assertEqual(self.brand.models.count(), 1)
        self.assertEqual(self.brand.models.first().name, "X5")


class CarBrandReportModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="testuser@example.com"
        )
        self.report = CarBrandReport.objects.create(
            user=self.user,
            brand_name="Tesla",
            message="Додавайте більше електрокарів",
        )

    def test_car_brand_report_creation(self):
        self.assertEqual(self.report.user.username, "testuser")
        self.assertEqual(self.report.brand_name, "Tesla")
        self.assertEqual(self.report.message, "Додавайте більше електрокарів")
        self.assertIsNotNone(self.report.created_at)

    def test_report_user_relationship(self):
        self.assertEqual(self.user.carbrandreport_set.count(), 1)
        self.assertEqual(self.user.carbrandreport_set.first().brand_name, "Tesla")
