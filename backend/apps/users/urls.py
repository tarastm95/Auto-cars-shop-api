from django.urls import path
from .views import UserListView, UserDetailView, BanUserView

urlpatterns = [
    # Список користувачів (доступно лише для адміністраторів)
    path('users/', UserListView.as_view(), name='user-list'),

    # Детальна інформація про користувача (доступно лише для адміністраторів)
    # <int:pk> — ID користувача
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Заблокувати/розблокувати користувача
    # <int:pk> — ID користувача
    path('ban-user/<int:pk>/', BanUserView.as_view(), name='ban_user'),
]
