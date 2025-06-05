import os
import io
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cryptography.fernet import Fernet
from .models import EncryptedFile, UserLog
from .serializers import EncryptedFileSerializer, UserLogSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView



class UploadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        file_key = Fernet.generate_key()
        encrypted_file_key = settings.FERNET_MASTER.encrypt(file_key)

        fernet = Fernet(file_key)
        encrypted_data = fernet.encrypt(file.read())

        encrypted_filename = f"{file.name}.enc"
        file_path = os.path.join('media/encrypted', encrypted_filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

        encrypted_file = EncryptedFile.objects.create(
            owner=request.user,
            file=f'encrypted/{encrypted_filename}',
            filename_original=file.name,
            key=encrypted_file_key
        )

        #  Log uploadistvis
        UserLog.objects.create(
            user=request.user,
            action='UPLOAD',
            description=f"Uploaded file: {file.name}"
        )

        serializer = EncryptedFileSerializer(encrypted_file, context={'request': request})
        return Response(serializer.data)



class DownloadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            encrypted_file = EncryptedFile.objects.get(pk=pk, owner=request.user)
        except EncryptedFile.DoesNotExist:
            raise Http404("File not found")

        try:
            decrypted_file_key = settings.FERNET_MASTER.decrypt(encrypted_file.key)
            fernet = Fernet(decrypted_file_key)

            file_path = encrypted_file.file.path

            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            # counteri downloadistvis
            encrypted_file.download_count += 1
            encrypted_file.save()

            # logebistvis
            UserLog.objects.create(
                user=request.user,
                action='DOWNLOAD',
                description=f'Downloaded file: {encrypted_file.filename_original}'
            )

            response = FileResponse(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                filename=encrypted_file.filename_original
            )
            return response

        except Exception as e:
            return Response(
                {"detail": "File could not be downloaded/not found on my media :)"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class FilePagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'page_size'
    max_page_size = 100


# List User Files
# vincaa mflobeli is xedavs sakutar uploaded filebs
# filtrebi davamate, testingze mushaobs mara mainc maxsovdes ro rame aq )))

class EncryptedFileListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EncryptedFileSerializer
    pagination_class = FilePagination

    def get_queryset(self):
        sort_order = self.request.query_params.get('sort', 'asc').lower()
        extension = self.request.query_params.get('ext', None)

        files = EncryptedFile.objects.filter(owner=self.request.user)

        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            files = files.filter(filename_original__endswith=extension)

        if sort_order == 'desc':
            files = files.order_by('-filename_original')
        else:
            files = files.order_by('filename_original')

        return files

class DeleteEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            encrypted_file = EncryptedFile.objects.get(pk=pk, owner=request.user)
        except EncryptedFile.DoesNotExist:
            raise Http404("File not found")

        # Encrypted file washla
        file_path = encrypted_file.file.path
        if os.path.exists(file_path):
            os.remove(file_path)

        # model instance washlac database-dan
        encrypted_file.delete()

        return Response({"message": "File deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class UserLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = UserLog.objects.filter(user=request.user)
        serializer = UserLogSerializer(logs, many=True)
        return Response(serializer.data)
    
