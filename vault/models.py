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




class UserLog(models.Model):
    ACTION_CHOICES = [
        ('UPLOAD', 'Upload'),
        ('DOWNLOAD', 'Download'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
