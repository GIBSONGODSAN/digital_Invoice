import uuid
import bcrypt
from django.db import models
from django.utils import timezone
from .methods import encrypt_password

# USER MODEL
class CustomUser(models.Model):
    Roles = [
        ("employee", "employee"),
        ("admin", "admin"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, default="")
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=255,choices=Roles, default="employee")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.email

# EXCEL DATA MODEL
class PlantInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.CharField(max_length=255, null=True, blank=True, unique=True)

class ProjectInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.CharField(max_length=255, null=True, blank=True)
    project_wps = models.CharField(max_length=255, null=True, blank=True)
    plant = models.ForeignKey(PlantInfo, on_delete=models.CASCADE, null=True, blank=True, max_length=255)

    
class SentDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.CharField(max_length=255, null=True, blank=True)
    project = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)


class ScheduleDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filepath = models.TextField(max_length=255, null=True, blank=True)
    plant = models.CharField(max_length=255, null=True, blank=True)
    project = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    email = models.EmailField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    email_body = models.TextField(max_length=255, null=True, blank=True)
