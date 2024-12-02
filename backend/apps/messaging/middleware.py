from jwt import decode as jwt_decode, exceptions as jwt_exceptions
from rest_framework_simplejwt.settings import api_settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        payload = jwt_decode(token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
        user_id = payload.get('user_id')
        return User.objects.get(id=user_id)
    except (User.DoesNotExist, jwt_exceptions.InvalidTokenError):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        token = None

        # Парсимо токен із query string
        if 'token=' in query_string:
            token = query_string.split('token=')[1]

        # Визначаємо користувача
        scope['user'] = await get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)
