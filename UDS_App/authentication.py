from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        email = validated_token['email']
        return CustomUser.objects.get(id=email)