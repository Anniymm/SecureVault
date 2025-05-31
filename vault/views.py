import os
import io
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from cryptography.fernet import Fernet
from .models import EncryptedFile
from .serializers import EncryptedFileSerializer
from rest_framework import status

class UploadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES['file']
        
        # random key davageneriro da master_key gavuketo encrypt mere 
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

        serializer = EncryptedFileSerializer(encrypted_file, context={'request': request})
        return Response(serializer.data)


class DownloadEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            encrypted_file = EncryptedFile.objects.get(pk=pk, owner=request.user)
        except EncryptedFile.DoesNotExist:
            raise Http404("File not found")

        # master key-it decrypt
        decrypted_file_key = settings.FERNET_MASTER.decrypt(encrypted_file.key)
        fernet = Fernet(decrypted_file_key)

        file_path = encrypted_file.file.path

        with open(file_path, 'rb') as f:
                encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        # download_count update
        encrypted_file.download_count += 1
        encrypted_file.save()

        response = FileResponse(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            filename=encrypted_file.filename_original
        )
        return response



# List User Files
# vincaa mflobeli is xedavs sakutar uploaded filebs
# filtrebi davamate, testingze mushaobs mara mainc maxsovdes ro rame aq )))

class EncryptedFileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # query paramsebi
        sort_order = request.query_params.get('sort', 'asc').lower()
        extension = request.query_params.get('ext', None)
        files = EncryptedFile.objects.filter(owner=request.user)
        if extension:
            # wertilic ro iyos an ar iyos wertili 
            if not extension.startswith('.'):
                extension = '.' + extension
            files = files.filter(filename_original__endswith=extension)

        # ascending da descending
        if sort_order == 'desc':
            files = files.order_by('-filename_original')
        else:
            files = files.order_by('filename_original')

        serializer = EncryptedFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)



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