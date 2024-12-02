from rest_framework import generics
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import CarDealer
from .serializers import CarDealerSerializer
from configs.permissions import IsManagerOrAdministrator

class CarDealerListView(generics.ListAPIView):
    queryset = CarDealer.objects.all()
    serializer_class = CarDealerSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

class CarDealerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = CarDealer.objects.all()
    serializer_class = CarDealerSerializer
    permission_classes = [IsAuthenticated]

class CarDealerCreateView(CreateAPIView):
    queryset = CarDealer.objects.all()
    serializer_class = CarDealerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
