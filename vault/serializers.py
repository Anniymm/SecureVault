from rest_framework import serializers
from .models import EncryptedFile
from django.urls import reverse

class EncryptedFileSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = EncryptedFile
        fields = ['id', 'filename_original', 'uploaded_at', 'download_url', 'download_count']
        read_only_fields = ['download_url', 'download_count']
    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('vault:download_encrypted_file', kwargs={'pk': obj.pk})
            )
        return None



# class FileActivityLogSerializer(serializers.ModelSerializer):
#     file_name = serializers.CharField(source='file.filename_original', read_only=True)

#     class Meta:
#         model = FileActivityLog
#         fields = ['id', 'file_name', 'action', 'timestamp', 'details']