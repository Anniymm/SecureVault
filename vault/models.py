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

    

    def __str__(self):
        return self.filename_original



# class FileActivityLog(models.Model):
#     ACTION_CHOICES = [
#         ('upload', 'Uploaded'),
#         ('download', 'Downloaded'),
#         ('delete', 'Deleted'),
#         ('view', 'Viewed'),
#         # jerjerobit eseni minda
#     ]

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='file_logs')
#     files = models.ForeignKey('EncryptedFile', on_delete=models.CASCADE, related_name='logs')
#     action = models.CharField(max_length=20, choices=ACTION_CHOICES)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     details = models.TextField(blank=True)  # Optional details

#     def __str__(self):
#         return f"{self.user.username} {self.action} {self.file.filename_original} at {self.timestamp}"

