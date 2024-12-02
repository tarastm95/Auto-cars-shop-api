from rest_framework import serializers
from .models import CarModel, CarBrand, CarBrandReport
from django.db.models import Count

class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = ['id', 'name']

class CarModelSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=CarBrand.objects.all())

    class Meta:
        model = CarModel
        fields = ['id', 'name', 'brand']

class CarBrandReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrandReport
        fields = ['brand_name', 'message']
