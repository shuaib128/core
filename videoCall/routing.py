# routing.py
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chat/call/', ChatConsumer.as_asgi()),
]