from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import CarBrand, CarModel
from .serializers import CarBrandSerializer, CarModelSerializer, CarBrandReportSerializer
from configs.permissions import IsManagerOrAdministrator, IsSellerOrAdministrator

class CarBrandListCreateView(generics.ListCreateAPIView):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

    def perform_create(self, serializer):
        serializer.save()

class CarModelListCreateView(generics.ListCreateAPIView):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

    def perform_create(self, serializer):
        serializer.save()

class CarBrandReportView(generics.GenericAPIView):
    permission_classes = [IsSellerOrAdministrator]

    def post(self, request, *args, **kwargs):
        serializer = CarBrandReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save(user=request.user)

            send_mail(
                subject=f"Новий запит про додавання бренду: {report.brand_name}",
                message=f"Користувач {request.user.username} повідомляє про відсутність бренду {report.brand_name}. Повідомлення: {report.message or 'Без коментарів.'}",
                from_email='no-reply@example.com',
                recipient_list=['tarasmazepa95@gmail.com'],
            )

            return Response({'detail': 'Запит успішно відправлений!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
