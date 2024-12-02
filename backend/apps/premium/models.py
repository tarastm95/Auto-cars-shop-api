import uuid
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings
from apps.users.models import User

class PremiumToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='premium_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"PremiumToken for {self.user.email}"
