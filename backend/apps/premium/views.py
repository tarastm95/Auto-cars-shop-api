from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.users.models import User
from .models import PremiumToken
from .serializers import PremiumTokenSerializer
from configs.permissions import IsManagerOrAdministrator

class UpgradeToPremiumView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.is_premium:
            return Response(
                {"detail": "User is already a premium member."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_premium = True
        user.save()

        return Response(
            {"detail": f"User {user.email} has been upgraded to premium."},
            status=status.HTTP_200_OK
        )

class ActivatePremiumView(GenericAPIView):
    serializer_class = PremiumTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        try:
            premium_token = PremiumToken.objects.get(token=token, is_used=False)

            premium_token.user.is_premium = True
            premium_token.user.save()

            premium_token.is_used = True
            premium_token.save()

            return Response(
                {"detail": f"User {premium_token.user.email} has been upgraded to premium."},
                status=status.HTTP_200_OK
            )
        except PremiumToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )

class GeneratePremiumTokenView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManagerOrAdministrator]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if PremiumToken.objects.filter(user=user, is_used=False).exists():
            return Response({"detail": "Token already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)

        token = PremiumToken.objects.create(user=user)

        return Response(
            {"detail": f"Token created for user {user.email}.", "token": token.token},
            status=status.HTTP_201_CREATED
        )
