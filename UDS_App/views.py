from io import BytesIO
import re
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Plant_Project_Info
from .serializers import InsertUserSerializer, ExcelDataSerializer
from .methods import encrypt_password
from .forms import ExcelUploadForm
from rest_framework.parsers import FileUploadParser
import pandas as pd
from django.shortcuts import render, redirect

import logging
logger = logging.getLogger(__name__)

#SIGN IN API
class SignInAPIView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            user = CustomUser.objects.get(email=email)
            encryptPassword=encrypt_password(password)
            if (user.password == encryptPassword):
                print(user.password)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(e)
            return Response({'message': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#SIGN UP API / CREATE USER API
class CustomUserCreateView(APIView):
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)  
        serializer = InsertUserSerializer(data=request.data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            CustomUser.objects.create(
                email=serializer.validated_data.get('email'),
                password=encrypted_password,
                first_name=serializer.validated_data.get('first_name'),
                last_name=serializer.validated_data.get('last_name'),
                profile_image=serializer.validated_data.get('profile_image'),
                role=serializer.validated_data.get('role'),
                is_active=serializer.validated_data.get('is_active'),
                is_staff=serializer.validated_data.get('is_staff'),
                created_by=serializer.validated_data.get('created_by'),
                modified_by=serializer.validated_data.get('modified_by'),
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#BULK INSERT API
class ExcelUploadAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("Request Data:", request.data)
            excel_file = request.data.get('file')
            if excel_file:
                file_content = BytesIO(excel_file.read())
                df = pd.read_excel(file_content)
                df.columns = [f"{col}_{i}" if df.columns.duplicated().any() else col for i, col in enumerate(df.columns)]
                records = df.to_dict('records')
                serializer = ExcelDataSerializer(data=records, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    print("Serializer Errors:", serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Exception:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def clean_column_name(col):
    col = str(col)
    col = col.replace(' ', '_')
    col = col.replace('.', '_')
    col = col.replace('-', '_')
    col = col.replace('(', '')
    col = col.replace(')', '')
    col = col.replace('/', '_')
    col = col.replace('%', 'percent')
    col = col.replace('?', '')
    col = col.replace('\'', '')
    col = col.replace('\"', '')
    col = col.replace('&', 'and')