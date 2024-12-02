from rest_framework.permissions import IsAuthenticated
from configs.permissions import IsAdministrator, IsManagerOrAdministrator
from apps.users.models import User
from apps.users.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import generics, status

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdministrator]

class BanUserView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAdministrator]

    def get_object(self):
        try:
            return User.objects.get(pk=self.kwargs['pk'])
        except User.DoesNotExist:
            return Response({"error": "Користувача не знайдено."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        user = self.get_object()

        if user.role in ['seller', 'buyer']:
            user.is_active = False
            user.save()

            return Response({"detail": f"Користувач {user.username} заблокований."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Користувач не є продавцем або покупцем."}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        if user.role in ['seller', 'buyer']:
            user.is_active = True
            user.save()

            return Response({"detail": f"Користувач {user.username} розблокований."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Користувач не є продавцем або покупцем."}, status=status.HTTP_400_BAD_REQUEST)
