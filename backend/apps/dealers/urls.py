from django.urls import path
from .views import CarDealerListView, CarDealerDetailView, CarDealerCreateView

urlpatterns = [
    # Список автосалонів
    path('dealers/', CarDealerListView.as_view(), name='dealer-list'),

    # Деталі автосалону
    path('dealers/<int:pk>/', CarDealerDetailView.as_view(), name='dealer-detail'),

    # Додати автосалон
    path('dealers/create/', CarDealerCreateView.as_view(), name='dealer-detail'),
]
