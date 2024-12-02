from rest_framework import serializers
from .models import CarDealer

class CarDealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDealer
        fields = ['id', 'name', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']