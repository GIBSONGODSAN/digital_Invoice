from io import BytesIO
from zipfile import ZipFile
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Plant_Project_Info
from .serializers import InsertUserSerializer, ExcelDataSerializer, PlantSerializer, PlantProjectInfoSerializer
from .methods import encrypt_password, users_encode_token, admin_encode_token
from .authentication import UserTokenAuthentication, AdminTokenAuthentication
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
import pandas as pd
import os
import smtplib

logger = logging.getLogger(__name__)

#SIGN IN API
class SignInAPIView(APIView):

    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')
            user = CustomUser.objects.get(email=email)
            encryptPassword=encrypt_password(password)
            serializedUser = InsertUserSerializer(user)

            if (user.password == encryptPassword):
                if user.role == 'employee':
                    token = users_encode_token({"id": str(user.id), "role": user.role})
                else:
                    token = admin_encode_token({"id": str(user.id), "role": user.role})
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': str(token),
                    'access': str(refresh.access_token),
                    'data': serializedUser.data, 
                    'message': 'User logged in successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(e)
            return Response({'message': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

#SIGN UP API / CREATE USER API
class CustomUserCreateView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)  
        serializer = InsertUserSerializer(data=request.data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            return Response({'data':serializer.data, 'message':"User created Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#BULK INSERT API
class ExcelUploadAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            excel_file = data.get('file')
            if excel_file:
                file_content = BytesIO(excel_file.read())
                df = pd.read_excel(file_content)
                df.columns = [f"{col}_{i}" if df.columns.duplicated().any() else col for i, col in enumerate(df.columns)]
                records = df.to_dict('records')
                serializer = ExcelDataSerializer(data=records, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'data':serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
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
    col = col.replace('__', '_')
    col = col.lower()
    return col

#ZIP FILE UPLOAD API
class ZipDirectoryAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]

    def post(self, request):
        data = request.data
        directory_path = data.get('directory_path', '')
        to_email = data.get('to_email', '')

        if os.path.exists(directory_path):
            print("Directory exists")
            unique_name = datetime.now().strftime("%Y%m%d%H%M%S")
            zip_file_path = os.path.join("D:/", f'zipped_files_{unique_name}.zip')
            file_name = []
            print("Zipping files")
            with ZipFile(zip_file_path, 'w') as zip_file:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_name.append(file)
                        arcname = os.path.relpath(file_path, directory_path)
                        zip_file.write(file_path, arcname=arcname)
            print("Zipping completed")
            print("Sending email")
            email_subject = 'Zipped Files'
            email_body = 'Please find attached the zipped files.'

            msg = MIMEMultipart()
            msg.attach(MIMEText(email_body, 'plain'))
            print("Email body attached")
            with open(zip_file_path, 'rb') as attachment:
                attached_file = MIMEApplication(attachment.read(), _subtype="zip")
                attached_file.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_file_path))
                msg.attach(attached_file)

            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_username = 'gibson.25cs@licet.ac.in'
            smtp_password = 'NARSELmary1305@'
            print("Email being sent")
            # Send the email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, to_email, msg.as_string())
            print("Email sent")
            # Send a response indicating the file path and email status
            return Response({'data': file_name, 'message': 'Zip file created and email sent successfully.',
                             'zip_file_path': zip_file_path, 'to_email': to_email},
                            status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Directory does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
class ZipDirectoryAPIView2(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request):
        data = request.data
        directory_path = data.get('directory_path', '')
        files_to_zip = data.get('files', [])  

        if os.path.exists(directory_path):
            unique_name = datetime.now().strftime("%Y%m%d%H%M%S")
            zip_file_path = os.path.join("D:/", f'zipped_files_{unique_name}.zip')
            file_name = []

            with ZipFile(zip_file_path, 'w') as zip_file:
                for file in files_to_zip:
                    file_path = os.path.join(directory_path, file)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        file_name.append(file)
                        arcname = os.path.relpath(file_path, directory_path)
                        print(f"Adding to zip: {file_path} with arcname {arcname}")
                        zip_file.write(file_path, arcname=arcname)

                return Response({'data': file_name, 'message': 'Zip file created and email sent successfully.',
                                'zip_file_path': zip_file_path},
                                status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Directory does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
#FILE LIST API
class FileListAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request):
        data = request.data
        directory_path = data.get('directory_path', '')

        if os.path.exists(directory_path):
            contents = os.listdir(directory_path)
            file_list = [item for item in contents if os.path.isfile(os.path.join(directory_path, item))]
            directory_list = [item for item in contents if os.path.isdir(os.path.join(directory_path, item))]
            response_data = {
                'files': file_list,
                'directories': directory_list,
            }
            return Response({'data': response_data, 'message': "Files List is shown"}, status=200)
        else:
            return Response({'error': 'Directory does not exist'}, status=400)
        
#PLANT LIST API
class PlantListView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def get(self, request):
        if request.method == 'GET':
            queryset = Plant_Project_Info.objects.values('PLANT').distinct()
            # unique_plants = self.get_unique_plants(queryset)
            serializer = PlantSerializer(queryset, many=True)
            return Response({'data':serializer.data, 'message':"Plant details listed"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Please provide a valid request method.'}, status=status.HTTP_400_BAD_REQUEST)
    

#PLANT PROJECT LIST API   
class PlantProjectListView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def get(self, request):
        data = request.data
        plant_name = data.get('plant_name', None)

        if plant_name:
            queryset = Plant_Project_Info.objects.filter(PLANT=plant_name)
            serializer = PlantProjectInfoSerializer(queryset, many=True)
            return Response({"data":serializer.data, 'message':"Projects are listed"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Please provide a valid plant name.'}, status=status.HTTP_400_BAD_REQUEST)