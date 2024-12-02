from django.urls import path, include

urlpatterns = [
    path('', include('apps.users.urls')),
    path('', include('apps.cars.urls')),
    path('', include('apps.dealers.urls')),
    path('', include('apps.premium.urls')),
    path('', include('apps.brands.urls')),
    path('', include('apps.auth.urls')),
    path('', include('apps.currency.urls')),
]
