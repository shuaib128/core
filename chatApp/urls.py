from django.urls import path
from .views import CreateRetriveChatroom, ChatMessageSearchView

urlpatterns = [
    path('chatroom/', CreateRetriveChatroom.as_view(), name='CreateRetriveChatroom'),
    path('search/message/', ChatMessageSearchView.as_view()),
]