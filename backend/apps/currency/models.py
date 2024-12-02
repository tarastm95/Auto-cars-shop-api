from django.db import models

class ExchangeRate(models.Model):
    currency_from = models.CharField(max_length=3)  # Наприклад, "USD"
    currency_to = models.CharField(max_length=3)    # Наприклад, "EUR"
    rate = models.DecimalField(max_digits=10, decimal_places=4)  # Курс валюти
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення

    class Meta:
        unique_together = ('currency_from', 'currency_to')  # Унікальність пари валют

    def __str__(self):
        return f"{self.currency_from} to {self.currency_to} at {self.rate}"
