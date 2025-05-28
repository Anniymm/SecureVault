from django.urls import path
from .views import UploadEncryptedFileView, DownloadEncryptedFileView

urlpatterns = [
    path('upload/', UploadEncryptedFileView.as_view(), name='upload-encrypted-file'),
    path('download/<int:pk>/', DownloadEncryptedFileView.as_view(), name='download-encrypted-file'),
]
