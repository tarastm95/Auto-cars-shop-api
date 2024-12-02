from datetime import timedelta
from django.utils.timezone import now
from rest_framework import serializers
from apps.currency.models import ExchangeRate
from apps.brands.models import CarBrand, CarModel
from .models import CarAd
import logging

logger = logging.getLogger(__name__)

class CarAdSerializer(serializers.ModelSerializer):
    brand = serializers.CharField()
    model = serializers.CharField()
    converted_prices = serializers.SerializerMethodField()

    class Meta:
        model = CarAd
        fields = [
            "title",
            "description",
            "price",
            "year",
            "currency",
            "brand",
            "model",
            "city",
            "country",
            "converted_prices"
        ]

    def validate_brand_and_model(self, brand_name: str, model_name: str):
        logger.debug(f"Перевіряємо бренд: {brand_name} і модель: {model_name}")
        brand = CarBrand.objects.filter(name=brand_name).first()
        if not brand:
            logger.error(f"Бренд '{brand_name}' не знайдено.")
            raise serializers.ValidationError({"brand": f"Бренд '{brand_name}' не знайдено."})
        model = CarModel.objects.filter(name=model_name, brand_id=brand.id).first()
        if not model:
            logger.error(f"Модель '{model_name}' не існує для бренду '{brand_name}'.")
            raise serializers.ValidationError(
                {"model": f"Модель '{model_name}' не існує для бренду '{brand_name}'."}
            )
        logger.debug(f"Бренд '{brand_name}' і модель '{model_name}' підтверджені.")
        return brand, model

    def get_converted_prices(self, obj):
        currencies = ['USD', 'EUR', 'UAH']
        converted_prices = {}
        for currency_to in currencies:
            try:
                if obj.currency == currency_to:
                    converted_prices[currency_to] = obj.price
                else:
                    exchange_rate = ExchangeRate.objects.get(currency_from=obj.currency, currency_to=currency_to)
                    converted_price = obj.price * exchange_rate.rate
                    converted_prices[currency_to] = round(converted_price, 2)
            except ExchangeRate.DoesNotExist:
                logger.error(f"Курс обміну для {obj.currency} -> {currency_to} не знайдено.")
                converted_prices[currency_to] = None
        return converted_prices

    def validate(self, data):
        brand_name = data.get("brand")
        model_name = data.get("model")
        if not brand_name:
            raise serializers.ValidationError({"brand": "Бренд є обов'язковим."})
        if not model_name:
            raise serializers.ValidationError({"model": "Модель є обов'язковою."})
        brand, model = self.validate_brand_and_model(brand_name, model_name)
        data["brand"] = brand
        data["model"] = model
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        logger.debug(f"Початок створення оголошення для користувача: {user}")
        if not user.is_premium:
            active_ads_count = CarAd.objects.filter(user=user, status="active").count()
            if active_ads_count >= 1:
                logger.error(f"Базовий акаунт користувача {user} може мати лише одне активне оголошення.")
                raise serializers.ValidationError(
                    "Базовий акаунт може мати лише одне активне оголошення."
                )
        brand = validated_data.pop("brand")
        model = validated_data.pop("model")
        validated_data["brand_id"] = brand.id
        validated_data["model_id"] = model.id
        validated_data["user"] = user
        logger.debug(f"Дані для створення оголошення: {validated_data}")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        brand_name = validated_data.get("brand", instance.brand.name)
        model_name = validated_data.get("model", instance.model.name)
        logger.debug(f"Оновлення оголошення для бренду: {brand_name} і моделі: {model_name}")
        brand, model = self.validate_brand_and_model(brand_name, model_name)
        validated_data["brand"] = brand
        validated_data["model"] = model
        logger.debug(f"Оновлені дані оголошення: {validated_data}")
        return super().update(instance, validated_data)

class CarAdUpdateSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(required=False)
    model = serializers.CharField(required=False)

    class Meta:
        model = CarAd
        fields = [
            "title",
            "description",
            "price",
            "currency",
            "brand",
            "model",
            "status",
        ]

    def validate(self, data):
        brand_name = data.get('brand')
        model_name = data.get('model')
        if brand_name:
            try:
                brand = CarBrand.objects.get(name=brand_name)
            except CarBrand.DoesNotExist:
                raise serializers.ValidationError({"brand": "Цей бренд не існує."})
            data['brand'] = brand
        if model_name:
            if 'brand' not in data:
                ad = self.instance
                brand = ad.brand
            else:
                brand = data['brand']
            try:
                model = CarModel.objects.get(name=model_name, brand=brand)
            except CarModel.DoesNotExist:
                raise serializers.ValidationError({"model": "Ця модель не існує для обраного бренду."})
            data['model'] = model
        return data

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.model = validated_data.get('model', instance.model)
        if 'status' in validated_data:
            status = validated_data['status']
            if status == 'active' and instance.moderation_attempts < 3:
                instance.moderate_ad()
                if instance.moderation_status == 'approved':
                    instance.status = 'active'
                else:
                    instance.status = 'inactive'
            else:
                instance.status = status
        instance.save()
        return instance

class BlockCarAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarAd
        fields = ['status']

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if instance.status != 'inactive':
            raise serializers.ValidationError("Статус можна змінити тільки на 'inactive'.")
        instance.save()
        return instance

class CarAdStatsSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True)
    model = serializers.CharField(source='model.name', read_only=True)
    views_today = serializers.SerializerMethodField()
    views_this_week = serializers.SerializerMethodField()
    views_this_month = serializers.SerializerMethodField()
    regional_average_price = serializers.SerializerMethodField()
    national_average_price = serializers.SerializerMethodField()

    class Meta:
        model = CarAd
        fields = [
            'id', 'title', 'brand', 'model', 'price', 'currency', 'views_count',
            'views_today', 'views_this_week', 'views_this_month',
            'regional_average_price', 'national_average_price'
        ]

    def get_views_today(self, obj):
        return obj.views.filter(timestamp__gte=now() - timedelta(days=1)).count()

    def get_views_this_week(self, obj):
        return obj.views.filter(timestamp__gte=now() - timedelta(weeks=1)).count()

    def get_views_this_month(self, obj):
        return obj.views.filter(timestamp__gte=now() - timedelta(days=30)).count()

    def get_regional_average_price(self, obj):
        city = obj.city
        country = obj.country
        return obj.get_similar_ads_average_price(city=city, country=country)

    def get_national_average_price(self, obj):
        return obj.get_similar_ads_average_price(city=None, country=None)
