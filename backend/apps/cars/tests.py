from django.test import TestCase
from django.utils.timezone import now
from django.core.mail import EmailMessage
from unittest.mock import patch
from apps.users.models import User
from apps.cars.models import CarAd, CarAdView
from apps.brands.models import CarBrand, CarModel

class CarAdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="testuser@example.com"
        )
        self.brand = CarBrand.objects.create(name="Toyota")
        self.model = CarModel.objects.create(brand=self.brand, name="Camry")
        self.ad = CarAd.objects.create(
            user=self.user,
            title="Продається автомобіль",
            description="Чудовий стан",
            price=15000,
            year=2020,
            currency="USD",
            brand=self.brand,
            model=self.model,
            city="Київ",
            country="Україна",
        )

    def test_contains_profanity(self):
        self.assertTrue(self.ad.contains_profanity("spam"))
        self.assertFalse(self.ad.contains_profanity("чудовий стан"))

    @patch('django.core.mail.send_mail')
    def test_notify_seller_to_update(self, mock_send_mail):
        self.ad.notify_seller_to_update()
        mock_send_mail.assert_called_once_with(
            "Оголошення потребує змін",
            f"Ваше оголошення (ID {self.ad.id}) потребує змін через порушення політики.",
            "tarasmazepa95@gmail.com",
            [self.user.email],
        )

    @patch('django.core.mail.send_mail')
    def test_moderate_ad(self, mock_send_mail):
        self.ad.title = "spam title"
        self.ad.moderate_ad()
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.moderation_status, "pending")
        self.assertEqual(self.ad.status, "inactive")
        mock_send_mail.assert_called_once()

    def test_get_similar_ads_average_price(self):
        CarAd.objects.create(
            user=self.user,
            title="Ще одне авто",
            description="Відмінний стан",
            price=14000,
            year=2020,
            currency="USD",
            brand=self.brand,
            model=self.model,
            city="Київ",
            country="Україна",
        )
        average_price = self.ad.get_similar_ads_average_price(city="Київ")
        self.assertEqual(average_price, 14000)

    def test_save_method(self):
        self.ad.title = "scam offer"
        self.ad.save()
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.status, "inactive")
        self.assertEqual(self.ad.moderation_status, "pending")


class CarAdViewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123", email="testuser@example.com"
        )
        self.brand = CarBrand.objects.create(name="Toyota")
        self.model = CarModel.objects.create(brand=self.brand, name="Camry")
        self.ad = CarAd.objects.create(
            user=self.user,
            title="Продається автомобіль",
            description="Чудовий стан",
            price=15000,
            year=2020,
            currency="USD",
            brand=self.brand,
            model=self.model,
            city="Київ",
            country="Україна",
        )
        self.view = CarAdView.objects.create(car_ad=self.ad, timestamp=now())

    def test_view_creation(self):
        self.assertEqual(self.view.car_ad, self.ad)
        self.assertIsNotNone(self.view.timestamp)

    def test_view_ordering(self):
        earlier_view = CarAdView.objects.create(
            car_ad=self.ad, timestamp=now().replace(day=1)
        )
        views = CarAdView.objects.all()
        self.assertEqual(views.first(), self.view)
        self.assertEqual(views.last(), earlier_view)
