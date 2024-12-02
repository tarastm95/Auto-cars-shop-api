from rest_framework.permissions import BasePermission
from apps.cars.models import CarAd

class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'buyer'

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'seller'

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'manager'

class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'administrator'

class IsManagerOrAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated and
                (request.user.role == 'manager' or
                 request.user.is_superuser)
        )

class IsSellerOrAdministrator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.role == 'seller' or
             request.user.is_superuser)
        )

class IsAdminManagerOrPremium(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.is_staff:
            return True
        if user.is_authenticated and getattr(user, "role", None) == "manager":
            return True
        if user.is_authenticated and getattr(user, "is_premium", False):
            return True
        return False

class IsManagerOrOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'manager' or request.user.is_superuser:
            return True
        ad_id = view.kwargs.get('pk')
        try:
            ad = CarAd.objects.get(id=ad_id)
        except CarAd.DoesNotExist:
            return False
        return ad.user == request.user
