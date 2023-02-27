from django.urls import path
from .views import MyAPIView

urlpatterns = [
    path('my-endpoint/', MyAPIView.as_view(), name='my-endpoint'),
]