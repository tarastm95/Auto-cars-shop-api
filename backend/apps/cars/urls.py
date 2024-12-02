from django.urls import path
from .views import (
    CarAdListView, CarAdCreateView, CarAdDeleteView, CarAdUpdateView,
    CarAdReadOnlyView, CarAdFilterView, CarAdApproveView, BlockCarAdView,
    CarAdStatsView
)

urlpatterns = [
    # Список оголошень поточного користувача
    path('cars/ad/', CarAdListView.as_view(), name='car-list'),

    # Оголошення в режимі перегляду
    path('cars/ad/<int:pk>/view/', CarAdReadOnlyView.as_view(), name='car_ad_view'),

    # Створення нового оголошення
    path('cars/ad/create/', CarAdCreateView.as_view(), name='car-create'),

    # Видалення оголошення
    path('cars/ad/<int:pk>/delete/', CarAdDeleteView.as_view(), name='car-delete'),

    # Оновлення оголошення
    path('cars/ad/<int:pk>/update/', CarAdUpdateView.as_view(), name='update_car_ad'),

    # Блокування оголошення
    path('cars/ad/block/<int:pk>/', BlockCarAdView.as_view(), name='carad-block'),

    # Фільтрація оголошень
    path('cars/ad/filter/', CarAdFilterView.as_view(), name='carad-filter'),

    # Затвердження оголошення
    path('cars/ad/<int:pk>/approve/', CarAdApproveView.as_view(), name='carad-approve'),

    # Статистика переглядів оголошення
    path('cars/ad/<int:pk>/stats/', CarAdStatsView.as_view(), name='car_ad_stats'),
]
