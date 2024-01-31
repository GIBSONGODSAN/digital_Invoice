from django.urls import path
from .views import CustomUserCreateView, SignInAPIView, ExcelUploadAPIView, ZipDirectoryAPIView, PlantListView, PlantProjectListView, FileListAPIView, ZipDirectoryAPIView2

urlpatterns = [
    path('login/', SignInAPIView.as_view(), name='user-login'),
    path('create/', CustomUserCreateView.as_view(), name='create-customuser'),
    path('uploadexcel/', ExcelUploadAPIView.as_view(), name='upload_excel_api'),
    path('zipdirectory/', ZipDirectoryAPIView.as_view(), name='zip_directory'),
    path('plantlist/', PlantListView.as_view(), name='plant-list'),
    path('plantprojects/', PlantProjectListView.as_view(), name='plant-projects'),
    path('filelist/', FileListAPIView.as_view(), name='file-list'),
    path('zipdirectory2/', ZipDirectoryAPIView2.as_view(), name='zip_directory2'),
]
