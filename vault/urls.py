from django.urls import path
from .views import UploadEncryptedFileView, DownloadEncryptedFileView

app_name = "vault"   # need review for this 

urlpatterns = [
    path('upload/', UploadEncryptedFileView.as_view(), name='upload_encrypted_file'),
    path('download/<int:pk>/', DownloadEncryptedFileView.as_view(), name='download_encrypted_file'),
]
