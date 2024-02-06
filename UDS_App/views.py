from io import BytesIO
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, SentDetails, PlantInfo, ProjectInfo, ScheduleDetails
from .serializers import CustomUserSerializer, ExcelPlantSerializer, ExcelProjectSerializer
from .serializers import SentDetailsSerializer, SentDetailsViewSerializer, ScheduleDetailsSerializer
from .methods import encrypt_password, users_encode_token, admin_encode_token, zip_files, send_email
from .authentication import UserTokenAuthentication, AdminTokenAuthentication
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
import logging
import pandas as pd
import os

logger = logging.getLogger(__name__)

#SIGN IN API
class SignInAPIView(APIView):

    def post(self, request):
        try:
            data = request.data
            email = data.get("email")
            password = data.get("password")
            user = CustomUser.objects.get(email=email)
            encryptPassword = encrypt_password(password)
            serializedUser = CustomUserSerializer(user)

            if user.password == encryptPassword:
                if user.role == "employee":
                    token = users_encode_token({"id": str(user.id), "role": user.role})
                else:
                    token = admin_encode_token({"id": str(user.id), "role": user.role})
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "token": str(token),
                        "access": str(refresh.access_token),
                        "data": serializedUser.data,
                        "message": "User logged in successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(e)
            return Response({"message": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

#SIGN UP API / CREATE USER API
class UserDetailsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            return Response({'data': serializer.data, 'message': "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        paginator = Paginator(CustomUser.objects.all(), 10)  # Adjust page size as needed
        page = request.query_params.get('page', 1)
        result_page = paginator.get_page(page)
        serializer = CustomUserSerializer(result_page, many=True)
        return Response({'data': serializer.data, 'message': "User details listed successfully"}, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        data = request.data
        user = CustomUser.objects.get(pk=pk)
        serializer = CustomUserSerializer(user, data=data)
        
        if serializer.is_valid():
            raw_password = serializer.validated_data.get('password')
            encrypted_password = encrypt_password(raw_password)
            serializer.save(password=encrypted_password)
            return Response({'data': serializer.data, 'message': "User updated successfully"})
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return Response({'message': "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FileListAPI_Alter_View(APIView):
    authentication_classes = [UserTokenAuthentication]

    def post(self, request):
        data = request.data
        p_directory_path = data.get("directory_path", "")
        excluded_folders = "common"
        directory_path = (
            "/home/codoid/projects_hosting/uds_invoice_backend/documents/"
            + p_directory_path
        )
        # Check if the state folder exists
        if not os.path.exists(directory_path):
            print(f"The folder '{directory_path}' does not exist.")
            return Response({"message":f"The folder '{directory_path}' does not exist."}, status=502)

        # Get the list of all files in the state folder excluding specific folders
        full_files = []
        for root, dirs, files in os.walk(directory_path):
            dirs[:] = [d for d in dirs if d not in excluded_folders]
            print(root, dirs, files)
            for file in files:
                print(root)
                all_files = {}
                all_files["label"] = os.path.splitext(file)[0].upper()
                all_files["value"] = os.path.splitext(file)[0].upper()
                all_files["children"] = [
                    {"label": file, "value": os.path.join(root, file)}
                ]
                full_files.append(all_files)
                # Print the list of all files

        response_data = {"files": full_files}
        return Response(
            {"data": response_data, "message": "Files List is shown"}, status=200
        )
        #     return Response({'data': response_data, 'message': "Files List is shown"}, status=200)
        # else:
        #     return Response({'error': 'Directory does not exist'}, status=400)


#BULK INSERT API
class ExcelUploadAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            excel_file = data.get('file')
            if not excel_file:
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            file_content = BytesIO(excel_file.read())
            df = pd.read_excel(file_content)
            df.columns = [f"{col}_{i}" if df.columns.duplicated().any() else col for i, col in enumerate(df.columns)]
            records = df.to_dict('records')

            PlantInfo.objects.all().delete()
            ProjectInfo.objects.all().delete()

            serializerPlant = ExcelPlantSerializer(data=[{'plant': plant} for plant in set(record['plant'] for record in records)], many=True)
            if serializerPlant.is_valid():
                plants = serializerPlant.save()
                plantID = {plant['plant']: plant['id'] for plant in serializerPlant.data}
            else:
                return Response({'error': {'plant': serializerPlant.errors}}, status=status.HTTP_400_BAD_REQUEST)

            # Process and save project data with plant IDs
            df = pd.DataFrame(records)
            grouped_df = df.groupby('plant').agg({'project': list, 'project_wps': list}).reset_index()
            project_data = []

            for _, row in grouped_df.iterrows():
                plant_id = plantID.get(row['plant'])
                if plant_id is not None:
                    projects = row['project']
                    project_wps = row['project_wps']

                    for project, wps in zip(projects, project_wps):
                        project_item = {
                            'project': project,
                            'project_wps': wps,
                            'plant': plant_id,
                        }
                        project_data.append(project_item)
                else:
                    # Handle the case where plant_id is not found for the current plant name
                    print(f"Warning: Plant ID not found for plant {row['plant']}")
            

            serializerProject = ExcelProjectSerializer(data=project_data, many=True)
            if serializerProject.is_valid():
                serializerProject.save()
            else:
                return Response({'error': {'project': serializerProject.errors}}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': 'Data processed successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
             
class ZipDirectoryAPIView2(APIView):
    authentication_classes = [UserTokenAuthentication]

    def post(self, request):
        data = request.data
        isScheduled = data.get('isScheduled', False)

        if isScheduled:
            serializer = ScheduleDetailsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':serializer.data, 'message':"Scheduled details saved"}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            file_paths = data.get('file_paths', None)
            to_email = data.get('to_email', None)
            email_subject = data.get('email_subject', None)
            email_body = data.get('email_body', None)
            
            serializer = SentDetailsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':serializer.data, 'message':"Sent details saved"}, status=status.HTTP_201_CREATED)
            
            if not file_paths:
                return Response({'message': 'No file paths provided'}, status=status.HTTP_400_BAD_REQUEST)  
            
            if not to_email or not email_subject or not email_body:
                return Response({'message': 'Please provide to_email, email_subject, and email_body'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Call the zip function
            zip_file_path, file_names = zip_files(file_paths)

            # Call the email function
            try:
                send_email(to_email, email_subject, email_body, zip_file_path)
                return Response({'data': file_names, 'message': 'Zip file created and email sent successfully.',
                                'zip_file_path': zip_file_path},
                                status=status.HTTP_200_OK)
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                return Response({'message': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#PLANT LIST API
class PlantListView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def get(self, request):
        if request.method == 'GET':
            queryset = PlantInfo.objects.all()
            serializer = ExcelPlantSerializer(queryset, many=True)
            return Response({'data':serializer.data, 'message':"Plant details listed"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Please provide a valid request method.'}, status=status.HTTP_400_BAD_REQUEST)
    

#PLANT PROJECT LIST API   
class PlantProjectListView(APIView):
    authentication_classes = [UserTokenAuthentication]

    def get(self, params):
        data = params.data
        plantId = data.get('id', None)

        if plantId is not None:
            queryset = ProjectInfo.objects.filter(plant=plantId)
            print(queryset)
            serializer = ExcelProjectSerializer(queryset, many=True)
            
            return Response({"data": serializer.data, 'message': "Projects are listed"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Please provide a valid plant name.'}, status=status.HTTP_400_BAD_REQUEST)
        
class SentDetailsAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10  
        sent_details_list = SentDetails.objects.all()
        result_page = paginator.paginate_queryset(sent_details_list, request)
        serializer = SentDetailsViewSerializer(result_page, many=True)
        return Response({'data':serializer.data, 'message':"Sent Details listed"}, status=status.HTTP_200_OK)
    
class ScheduleDetailsAPIView(APIView):
    authentication_classes = [UserTokenAuthentication]
    def post(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10  
        schedule_details_list = ScheduleDetails.objects.all()
        result_page = paginator.paginate_queryset(schedule_details_list, request)
        serializer = ScheduleDetailsSerializer(result_page, many=True)
        return Response({'data':serializer.data, 'message':"Schedule Details listed"}, status=status.HTTP_200_OK)