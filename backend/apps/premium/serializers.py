from rest_framework import serializers

class PremiumTokenSerializer(serializers.Serializer):
    token = serializers.UUIDField()

