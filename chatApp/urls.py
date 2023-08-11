from django.urls import path
from .views import CreateRetriveChatroom, ChatMessageSearchView, ChatImageCreateAPIView, ChatVideoCreateAPIView, FinalizeUploadView

urlpatterns = [
    path('chatroom/', CreateRetriveChatroom.as_view(), name='CreateRetriveChatroom'),

    path('search/message/', ChatMessageSearchView.as_view()),

    path('add/media/image/', ChatImageCreateAPIView.as_view(), name='ChatImageCreateAPIView'),

    path('add/media/video/', ChatVideoCreateAPIView.as_view(), name='ChatVideoCreateAPIView'),

    path('add/media/video/finalize/', FinalizeUploadView.as_view(), name='FinalizeVideo'),
]