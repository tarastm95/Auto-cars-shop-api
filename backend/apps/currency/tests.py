from django.test import TestCase
from decimal import Decimal
from .models import ExchangeRate

class ExchangeRateModelTest(TestCase):
    def setUp(self):
        self.exchange_rate = ExchangeRate.objects.create(
            currency_from="USD",
            currency_to="EUR",
            rate=Decimal("0.8500"),
        )

    def test_exchange_rate_creation(self):
        self.assertEqual(self.exchange_rate.currency_from, "USD")
        self.assertEqual(self.exchange_rate.currency_to, "EUR")
        self.assertEqual(self.exchange_rate.rate, Decimal("0.8500"))

    def test_exchange_rate_string_representation(self):
        expected_string = "USD to EUR at 0.8500"
        self.assertEqual(str(self.exchange_rate), expected_string)

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            ExchangeRate.objects.create(
                currency_from="USD",
                currency_to="EUR",
                rate=Decimal("0.9000"),
            )

    def test_rate_update(self):
        old_updated_at = self.exchange_rate.updated_at
        self.exchange_rate.rate = Decimal("0.8600")
        self.exchange_rate.save()

        updated_rate = ExchangeRate.objects.get(id=self.exchange_rate.id)
        self.assertEqual(updated_rate.rate, Decimal("0.8600"))
        self.assertNotEqual(updated_rate.updated_at, old_updated_at)

    def test_create_different_currency_pair(self):
        new_exchange_rate = ExchangeRate.objects.create(
            currency_from="EUR",
            currency_to="GBP",
            rate=Decimal("0.7500"),
        )
        self.assertEqual(new_exchange_rate.currency_from, "EUR")
        self.assertEqual(new_exchange_rate.currency_to, "GBP")
        self.assertEqual(new_exchange_rate.rate, Decimal("0.7500"))
