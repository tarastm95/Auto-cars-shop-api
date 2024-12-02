from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ExchangeRate
from .serializers import ExchangeRateSerializer

class ExchangeRateView(APIView):
    def get(self, request, *args, **kwargs):
        rates = ExchangeRate.objects.all()
        serializer = ExchangeRateSerializer(rates, many=True)
        return Response(serializer.data)

