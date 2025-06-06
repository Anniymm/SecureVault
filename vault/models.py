from django.db import models
from django.conf import settings 
from datetime import timezone

class EncryptedFile(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    file = models.FileField(upload_to='encrypted/')
    filename_original = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    key = models.BinaryField()
    download_count = models.IntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.filename_original

