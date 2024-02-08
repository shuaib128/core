from django.urls import path
from .views import CreateRetriveChatroom

urlpatterns = [
    path('chatroom/', CreateRetriveChatroom.as_view(), name='CreateRetriveChatroom'),
]
