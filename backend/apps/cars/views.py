from django.core.mail import send_mail
from rest_framework import generics, status, mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CarAd, CarAdView
from .serializers import CarAdSerializer, CarAdUpdateSerializer, BlockCarAdSerializer, CarAdStatsSerializer
from configs.permissions import  IsManagerOrAdministrator, IsSellerOrAdministrator,  IsManagerOrOwner

class CarAdListView(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = CarAdSerializer
    permission_classes = [IsAuthenticated, IsSellerOrAdministrator]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'administrator':
            return CarAd.objects.all()
        return CarAd.objects.filter(user=user).exclude(status="inactive")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class CarAdCreateView(CreateAPIView):
    queryset = CarAd.objects.all()
    serializer_class = CarAdSerializer

    def perform_create(self, serializer):
        car_ad = serializer.save()
        car_ad.moderate_ad()
        return Response({"detail": "Оголошення на модерації."}, status=status.HTTP_201_CREATED)

class CarAdDeleteView(generics.DestroyAPIView):
    queryset = CarAd.objects.all()
    serializer_class = CarAdSerializer
    permission_classes = [IsManagerOrAdministrator]

    def delete(self, request, *args, **kwargs):
        try:
            car_ad = self.get_object()
            car_ad.delete()
            return Response({"detail": "Car advertisement deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except CarAd.DoesNotExist:
            return Response({"error": "Car advertisement not found."}, status=status.HTTP_404_NOT_FOUND)

class CarAdUpdateView(UpdateAPIView):
    queryset = CarAd.objects.all()
    serializer_class = CarAdUpdateSerializer

    def perform_update(self, serializer):
        car_ad = serializer.save()
        if car_ad.moderation_attempts < 3:
            car_ad.moderate_ad()
            if car_ad.moderation_status == 'approved':
                car_ad.status = 'active'
                car_ad.save()
            return Response({"detail": "Оголошення оновлено та на модерації."}, status=status.HTTP_200_OK)
        else:
            car_ad.status = "inactive"
            car_ad.save()
            return Response({"detail": "Оголошення заблоковано через перевищення кількості спроб."}, status=status.HTTP_400_BAD_REQUEST)

class CarAdReadOnlyView(RetrieveAPIView):
    queryset = CarAd.objects.all()
    serializer_class = CarAdSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        car_ad = self.get_object()
        CarAdView.objects.create(car_ad=car_ad)
        car_ad.views_count += 1
        car_ad.save(update_fields=["views_count"])
        return super().get(request, *args, **kwargs)

class CarAdFilterView(generics.ListAPIView):
    serializer_class = CarAdSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CarAd.objects.all()
        brand = self.request.query_params.get('brand', None)
        status = self.request.query_params.get('status', None)
        if brand:
            queryset = queryset.filter(brand__iexact=brand)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

class CarAdApproveView(APIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

    def patch(self, request, pk):
        try:
            ad = CarAd.objects.get(id=pk)
            if ad.status == 'active' and ad.moderation_status == 'approved':
                return Response({"detail": "Оголошення вже підтверджене."}, status=status.HTTP_400_BAD_REQUEST)
            ad.status = 'active'
            ad.moderation_status = 'approved'
            ad.save()
            return Response(CarAdSerializer(ad).data, status=status.HTTP_200_OK)
        except CarAd.DoesNotExist:
            return Response({"detail": "Оголошення не знайдено."}, status=status.HTTP_404_NOT_FOUND)

class BlockCarAdView(generics.UpdateAPIView):
    queryset = CarAd.objects.all()
    serializer_class = BlockCarAdSerializer
    permission_classes = [IsAuthenticated, IsManagerOrOwner]

    def patch(self, request, *args, **kwargs):
        ad = self.get_object()
        if request.user.role != 'manager' and ad.user != request.user:
            raise PermissionDenied("У вас немає прав для виконання цієї операції.")
        ad.status = 'inactive'
        ad.save()
        return self.update(request, *args, **kwargs)

class CarAdStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            car_ad = CarAd.objects.get(pk=pk)
        except CarAd.DoesNotExist:
            return Response({'detail': 'Оголошення не знайдено.'}, status=status.HTTP_404_NOT_FOUND)

        regional_average_price = car_ad.get_similar_ads_average_price(city=car_ad.city, country=car_ad.country)
        national_average_price = car_ad.get_similar_ads_average_price(city=None, country=None)
        serializer = CarAdStatsSerializer(car_ad)
        stats_data = serializer.data
        stats_data['regional_average_price'] = regional_average_price
        stats_data['national_average_price'] = national_average_price

        return Response(stats_data)
