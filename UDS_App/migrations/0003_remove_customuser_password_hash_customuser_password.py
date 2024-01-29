# Generated by Django 5.0.1 on 2024-01-29 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UDS_App', '0002_remove_customuser_password_customuser_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='password_hash',
        ),
        migrations.AddField(
            model_name='customuser',
            name='password',
            field=models.CharField(default='', max_length=255),
        ),
    ]