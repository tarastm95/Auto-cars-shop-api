from django.core.mail import send_mail
from django.db import models
from django.db.models import Avg
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CarAd(models.Model):
    MODERATION_STATUSES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("blocked", "Blocked"),
        ("manual_review", "Manual Review"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("pending", "Pending"),
    ]

    BANNED_WORDS = ["spam", "fake", "scam", "banned", "prohibited"]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ads"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.PositiveIntegerField()
    currency = models.CharField(
        max_length=3,
        choices=[("USD", "USD"), ("EUR", "EUR"), ("UAH", "UAH")],
    )
    brand = models.ForeignKey(
        'brands.CarBrand', on_delete=models.SET_NULL, null=True, related_name="ads"
    )
    model = models.ForeignKey(
        'brands.CarModel', on_delete=models.SET_NULL, null=True, related_name="ads"
    )
    status = models.CharField(
        max_length=20,
        default="active",
        choices=STATUS_CHOICES,
    )
    views_count = models.PositiveIntegerField(default=0)
    views_today = models.PositiveIntegerField(default=0)
    views_this_week = models.PositiveIntegerField(default=0)
    views_this_month = models.PositiveIntegerField(default=0)
    moderation_status = models.CharField(
        max_length=20,
        choices=MODERATION_STATUSES,
        default="pending",
    )
    moderation_attempts = models.PositiveIntegerField(default=0)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def contains_profanity(self, text):
        return any(word in text.lower() for word in self.BANNED_WORDS)

    def notify_seller_to_update(self):
        recipient_email = self.user.email.strip()
        try:
            send_mail(
                "Оголошення потребує змін",
                f"Ваше оголошення (ID {self.id}) потребує змін через порушення політики.",
                "tarasmazepa95@gmail.com",
                [recipient_email],
            )
        except Exception as e:
            print(f"Помилка при надсиланні листа: {e}")

    def moderate_ad(self):
        if self.contains_profanity(self.title) or self.contains_profanity(self.description):
            self.moderation_attempts += 1
            if self.moderation_attempts >= 3:
                self.moderation_status = "blocked"
                self.status = "inactive"
                send_mail(
                    "Оголошення заблоковано",
                    f"Ваше оголошення ID {self.id} було заблоковано через повторні порушення.",
                    "noreply@example.com",
                    [self.user.email],
                )
            else:
                self.moderation_status = "pending"
                self.notify_seller_to_update()
        else:
            self.moderation_status = "approved"
            self.status = "active"

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.contains_profanity(self.title) or self.contains_profanity(self.description):
            self.status = "inactive"
            self.moderation_status = "pending"
            self.moderation_attempts += 1
            if self.moderation_attempts >= 3:
                self.moderation_status = "blocked"
                self.status = "inactive"
                send_mail(
                    "Оголошення заблоковано",
                    f"Ваше оголошення ID {self.id} було заблоковано через повторні порушення.",
                    "tarasmazepa95@gmail.com",
                    [self.user.email],
                )
            else:
                self.notify_seller_to_update()
        else:
            if self.moderation_status != "blocked":
                self.moderation_status = "approved"
                self.status = "active"

        super().save(*args, **kwargs)

    def get_similar_ads_average_price(self, city=None, country=None):
        if not self.year or not self.brand or not self.model:
            return None

        logger.debug(
            f"Обчислюємо середню ціну для автомобіля: {self.brand}, {self.model}, {self.year}, {self.city}, {self.country}")

        similar_ads = CarAd.objects.filter(
            brand=self.brand,
            model=self.model,
            year__gte=self.year - 1,
            year__lte=self.year + 1
        ).exclude(id=self.id)

        logger.debug(f"Знайдено оголошень після фільтрації за брендом і моделлю: {similar_ads.count()}")

        if city:
            similar_ads = similar_ads.filter(city=city)
            logger.debug(f"Знайдено оголошень після фільтрації за містом: {similar_ads.count()}")
        if country:
            similar_ads = similar_ads.filter(country=country)
            logger.debug(f"Знайдено оголошень після фільтрації за країною: {similar_ads.count()}")

        average_price = similar_ads.aggregate(average_price=Avg('price'))['average_price']

        logger.debug(f"Середня ціна: {average_price}")

        return average_price

class CarAdView(models.Model):
    car_ad = models.ForeignKey('CarAd', related_name='views', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-timestamp']
