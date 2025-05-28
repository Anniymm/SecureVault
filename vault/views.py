from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EncryptedFile
from .serializers import EncryptedFileSerializer
from cryptography.fernet import Fernet
import os
from django.http import FileResponse, Http404
import io

class UploadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES['file']
        key = Fernet.generate_key()
        fernet = Fernet(key)

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
            key=key
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

        fernet = Fernet(encrypted_file.key)
        file_path = encrypted_file.file.path

        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        
        response = FileResponse(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            filename=encrypted_file.filename_original
        )
        return response
