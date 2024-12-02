from django.urls import path
from .views import UpgradeToPremiumView, ActivatePremiumView, GeneratePremiumTokenView

urlpatterns = [
    # Оновлення користувача до преміум-статусу
    path('upgrade-to-premium/', UpgradeToPremiumView.as_view(), name='upgrade-to-premium'),

    # Активація преміум-статусу користувача
    path('premium/activate/', ActivatePremiumView.as_view(), name='activate-premium'),

    # Генерація токену для преміум-статусу
    path('premium/generate/', GeneratePremiumTokenView.as_view(), name='generate-premium-token'),
]
