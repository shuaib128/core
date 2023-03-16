from django.urls import path
from .views import UserCreateAPIView, UserView, LogoutView, SearchUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/', UserView.as_view(), name='UserView'),
    path('user/create/', UserCreateAPIView.as_view(), name='create_user'),
    path('user/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/logout/', LogoutView.as_view(), name='LogoutView'),
    path('user/search/', SearchUserView.as_view(), name='SearchUserView'),
]