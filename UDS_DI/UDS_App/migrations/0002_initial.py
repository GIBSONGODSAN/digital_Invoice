# Generated by Django 5.0.1 on 2024-01-30 06:28

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('UDS_App', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(default='', max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('profile_image', models.TextField(blank=True, null=True)),
                ('role', models.CharField(default='employee', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('modified_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Plant_Project_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PLANT', models.CharField(blank=True, max_length=255, null=True)),
                ('PROJECT', models.CharField(blank=True, max_length=255, null=True)),
                ('PROJECT_WPS', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]