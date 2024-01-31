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
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    modified_by = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.email

# EXCEL DATA MODEL
class Plant_Project_Info(models.Model):
    PLANT = models.CharField(max_length=255, null=True, blank=True)
    PROJECT = models.CharField(max_length=255, null=True, blank=True)
    PROJECT_WPS = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.PLANT