from rest_framework import serializers
from .models import CustomUser
from .methods import encrypt_password

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email')

class InsertUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'profile_image', 'role', 'is_active', 'is_staff',
            'created_at', 'modified_at', 'created_by', 'modified_by'
        ]

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        encrypted_password = encrypt_password(raw_password)
        validated_data['password_hash'] = encrypted_password

        user = CustomUser.objects.create(**validated_data)
        return user
