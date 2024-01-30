from django.urls import path
from .views import CustomUserCreateView, SignInAPIView, ExcelUploadAPIView

urlpatterns = [
    path('login/', SignInAPIView.as_view(), name='user-login'),
    path('create/', CustomUserCreateView.as_view(), name='create-customuser'),
    path('uploadexcel/', ExcelUploadAPIView.as_view(), name='upload_excel_api'),

]
