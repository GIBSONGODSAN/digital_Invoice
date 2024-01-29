from django.urls import path
from .views import CustomUserCreateView, SignInAPIView

urlpatterns = [
    path('login/', SignInAPIView.as_view(), name='user-login'),
    path('create/', CustomUserCreateView.as_view(), name='create-customuser'),
]
