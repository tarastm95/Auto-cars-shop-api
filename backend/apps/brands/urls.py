from django.urls import path
from .views import CarBrandListCreateView, CarModelListCreateView, CarBrandReportView

urlpatterns = [
    # Список та створення брендів
    path('brands/', CarBrandListCreateView.as_view(), name='car-brand-list-create'),

    # Список та створення моделей автомобілів
    path('models/', CarModelListCreateView.as_view(), name='car-model-list-create'),

    # Звіт про додавання нового бренду
    path('report/', CarBrandReportView.as_view(), name='car-brand-report'),
]
