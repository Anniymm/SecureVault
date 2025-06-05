from rest_framework import serializers
from .models import EncryptedFile, UserLog
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


class UserLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = ['id', 'action', 'description', 'timestamp']