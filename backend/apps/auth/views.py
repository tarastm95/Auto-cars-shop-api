from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from configs.permissions import IsAdministrator
from .serializers import BuyerRegisterSerializer, SellerRegisterSerializer, ManagerRegisterSerializer

class BuyerRegisterView(CreateAPIView):
    serializer_class = BuyerRegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Покупець успішно зареєстрований!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellerRegisterView(CreateAPIView):
    serializer_class = SellerRegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Продавець успішно зареєстрований!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManagerRegisterView(CreateModelMixin, GenericAPIView):
    serializer_class = ManagerRegisterSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
