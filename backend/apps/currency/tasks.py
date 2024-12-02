# apps/currency/tasks.py

from celery import shared_task
import requests
from .models import ExchangeRate
from datetime import datetime


@shared_task
def fetch_exchange_rates():
    print("Fetching exchange rates...")
    url = "https://api.privatbank.ua/p24api/exchange_rates?json&date=" + datetime.now().strftime("%d.%m.%Y")
    response = requests.get(url)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")

    if response.status_code == 200:
        data = response.json()
        if 'exchangeRate' in data:
            eur_uah_rate = None
            usd_uah_rate = None

            # Список валют, які потрібно зберігати
            currencies_to_save = [
                ('EUR', 'UAH'),
                ('USD', 'UAH'),
                ('EUR', 'USD'),
                ('USD', 'EUR')
            ]

            # Спочатку зберігаємо курси валют, перевіряючи EUR/UAH та USD/UAH
            for rate in data['exchangeRate']:
                print(f"Processing rate: {rate}")
                currency_from = rate.get('currency')
                currency_to = rate.get('toCurrency', 'UAH')
                rate_value = rate.get('saleRateNB')

                if not currency_from or not rate_value:
                    print("Invalid rate data, skipping...")
                    continue

                # Перевіряємо, чи є цей курс у списку валют для збереження
                if (currency_from, currency_to) not in currencies_to_save:
                    print(f"Skipping rate: {currency_from} to {currency_to}")
                    continue

                # Оновлення або створення курсу в базі
                obj, created = ExchangeRate.objects.update_or_create(
                    currency_from=currency_from,
                    currency_to=currency_to,
                    defaults={'rate': rate_value, 'updated_at': datetime.now()}
                )
                if created:
                    print(f"Created new exchange rate: {obj}")
                else:
                    print(f"Updated existing exchange rate: {obj}")

                # Перевіряємо, чи це курс для EUR/UAH та USD/UAH
                if currency_from == 'EUR' and currency_to == 'UAH':
                    eur_uah_rate = rate_value
                if currency_from == 'USD' and currency_to == 'UAH':
                    usd_uah_rate = rate_value

            # Якщо ми отримали курси для EUR/UAH та USD/UAH, обчислюємо EUR/USD та USD/EUR
            if eur_uah_rate and usd_uah_rate:
                # Розрахунок курсів EUR/USD та USD/EUR
                eur_usd_rate = eur_uah_rate / usd_uah_rate  # EUR/USD
                usd_eur_rate = usd_uah_rate / eur_uah_rate  # USD/EUR

                # Оновлення або створення курсів для EUR/USD та USD/EUR
                ExchangeRate.objects.update_or_create(
                    currency_from='EUR', currency_to='USD',
                    defaults={'rate': eur_usd_rate, 'updated_at': datetime.now()}
                )
                ExchangeRate.objects.update_or_create(
                    currency_from='USD', currency_to='EUR',
                    defaults={'rate': usd_eur_rate, 'updated_at': datetime.now()}
                )

                print(f"Calculated EUR/USD rate: {eur_usd_rate}")
                print(f"Calculated USD/EUR rate: {usd_eur_rate}")

    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

