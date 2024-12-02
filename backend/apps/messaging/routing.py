from django.urls import re_path
from .consumers import TestDriveConsumer

websocket_urlpatterns = [
    re_path(r'ws/test-drive/(?P<other_user>\w+)/$', TestDriveConsumer.as_asgi()),
]
