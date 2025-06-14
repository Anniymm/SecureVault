from datetime import datetime
import io
import json
import os
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cryptography.fernet import Fernet
from .models import EncryptedFile, UserLog
from .serializers import EncryptedFileSerializer, UserLogSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse


class UploadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EncryptedFileSerializer

    @extend_schema(
        summary="Upload and encrypt a file",
        request=None,
        responses={
            201: EncryptedFileSerializer,
            400: OpenApiResponse(description="No file provided."),
        }
    )
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
            key=encrypted_file_key,
            note=request.data.get('note', '')
        )

        UserLog.objects.create(
            user=request.user,
            action='UPLOAD',
            description=f"Uploaded file: {file.name}"
        )

        serializer = EncryptedFileSerializer(encrypted_file, context={'request': request})
        return Response(serializer.data, status=201)


class DownloadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Download and decrypt a file",
        responses={200: OpenApiResponse(description="File download stream"),
                   404: OpenApiResponse(description="File not found"),
                   500: OpenApiResponse(description="File could not be downloaded")}
    )
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

            encrypted_file.download_count += 1
            encrypted_file.save()

            UserLog.objects.create(
                user=request.user,
                action='DOWNLOAD',
                description=f'Downloaded file: {encrypted_file.filename_original}'
            )

            return FileResponse(
                io.BytesIO(decrypted_data),
                as_attachment=True,
                filename=encrypted_file.filename_original
            )

        except Exception:
            return Response(
                {"detail": "File could not be downloaded/not found on my media :)"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FilePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class EncryptedFileListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EncryptedFileSerializer
    pagination_class = FilePagination

    @extend_schema(
        summary="List encrypted files uploaded by the user",
        parameters=[],
        responses={200: EncryptedFileSerializer(many=True)}
    )
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

    @extend_schema(
        summary="Delete an encrypted file",
        responses={204: OpenApiResponse(description="File deleted successfully."),
                   404: OpenApiResponse(description="File not found.")}
    )
    def delete(self, request, pk):
        try:
            encrypted_file = EncryptedFile.objects.get(pk=pk, owner=request.user)
        except EncryptedFile.DoesNotExist:
            raise Http404("File not found")

        file_path = encrypted_file.file.path
        if os.path.exists(file_path):
            os.remove(file_path)

        encrypted_file.delete()

        UserLog.objects.create(
            user=request.user,
            action='DELETE',
            description=f'deleted file: {encrypted_file.filename_original}'
        )

        return Response({"message": "File deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class UserLogsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List user action logs",
        responses={200: UserLogSerializer(many=True)}
    )
    def get(self, request):
        logs = UserLog.objects.filter(user=request.user)
        serializer = UserLogSerializer(logs, many=True)
        return Response(serializer.data)


class ExportUserLogsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Export user logs as a JSON file ( Download the json file of logs )",
        responses={200: OpenApiResponse(description="JSON log file download."),
                   404: OpenApiResponse(description="Error generating log export.")}
    )
    def get(self, request):
        try:
            export_format = request.query_params.get('format', 'json').lower()

            logs = UserLog.objects.filter(user=request.user).order_by('-timestamp')
            log_data = [
                {
                    'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'action': log.action,
                    'description': log.description,
                }
                for log in logs
            ]

            filename = f"{request.user.username}_logs_{datetime.now().strftime('%Y-%m-%d')}.json"
            json_content = json.dumps(log_data, indent=3)
            response = HttpResponse(json_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            return Response({"detail": str(e)}, status=404)
