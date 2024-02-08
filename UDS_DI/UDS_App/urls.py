from django.urls import path
from .views import UserDetailsAPIView, SignInAPIView, ExcelUploadAPIView, PlantListView, PlantProjectListView, FileListAPI_Alter_View, ZipDirectoryAPIView2
from .views import SentDetailsAPIView, ScheduleDetailsAPIView

urlpatterns = [
    path('login/', SignInAPIView.as_view(), name='user-login'),
    path('user/', UserDetailsAPIView.as_view(), name='create-customuser'),  
    path('user/<uuid:pk>', UserDetailsAPIView.as_view(), name='create-customuser'),
    path('uploadexcel/', ExcelUploadAPIView.as_view(), name='upload_excel_api'),
    path('plantlist/', PlantListView.as_view(), name='plant-list'),
    path('plantprojects/', PlantProjectListView.as_view(), name='plant-projects'),
    path('filelist/', FileListAPI_Alter_View.as_view(), name='file-list'),
    path('createproject/', ZipDirectoryAPIView2.as_view(), name='zip_directory2'),
    path('sentdetails/', SentDetailsAPIView.as_view(), name='sent-details-api'),
    path('scheduledetails/', ScheduleDetailsAPIView.as_view(), name='sent-details-api'),
]
