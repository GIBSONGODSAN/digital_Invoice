from rest_framework import serializers
from .models import CustomUser, PlantInfo, ProjectInfo, SentDetails, ScheduleDetails

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = "__all__"
    
class ExcelPlantSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantInfo
        fields = ['id', 'plant']

class ExcelProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInfo
        fields = ['id', 'project', 'project_wps', 'plant']

class SentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentDetails
        fields = ['id', 'plant', 'project', 'region', 'date', 'time']

class SentDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentDetails
        ordering = ['date', 'time']
        fields = ['id', 'plant', 'project', 'region', 'date', 'time']

class ScheduleDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleDetails
        fields = ['id', 'filepath', 'plant', 'project', 'region', 'date', 'time', 'email', 'subject', 'email_body']