from django.db import models
from apps.users.models import User

class CarBrand(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    brand = models.ForeignKey(
        CarBrand, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class CarBrandReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
