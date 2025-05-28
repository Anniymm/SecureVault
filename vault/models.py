from django.db import models
from django.conf import settings

class EncryptedFile(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='encrypted_files'
    )
    file = models.FileField(upload_to='encrypted/')
    filename_original = models.CharField(max_length=255)
    key = models.BinaryField()  # encrypted key 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename_original} uploaded by {self.owner.email}"
