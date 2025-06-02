from django.urls import path
from .views import EncryptedFileListView, UploadEncryptedFileView, DownloadEncryptedFileView, DeleteEncryptedFileView

app_name = "vault"   # need review for this 

urlpatterns = [
    path('upload/', UploadEncryptedFileView.as_view(), name='upload_encrypted_file'),
    path('download/<int:pk>/', DownloadEncryptedFileView.as_view(), name='download_encrypted_file'),
    path('files/', EncryptedFileListView.as_view(), name='file-list'),
    path('delete/<int:pk>/', DeleteEncryptedFileView.as_view(), name='delete-encrypted-file'),
    # path('logs/', FileActivityLogListView.as_view(), name='file-activity-logs'),
]
