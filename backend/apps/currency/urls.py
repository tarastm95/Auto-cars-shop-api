from django.urls import path
from .views import ExchangeRateView

urlpatterns = [
    path('exchange-rates/', ExchangeRateView.as_view(), name='exchange_rates')
]
