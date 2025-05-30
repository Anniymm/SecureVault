from rest_framework import serializers
from .models import EncryptedFile
from django.urls import reverse

class EncryptedFileSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = EncryptedFile
        fields = ['id', 'filename_original', 'uploaded_at', 'download_url']

    def get_download_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(
                reverse('vault:download_encrypted_file', kwargs={'pk': obj.pk})
            )
        return None
