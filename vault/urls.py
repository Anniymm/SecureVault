from django.urls import path
from .views import EncryptedFileListView, ExportUserLogsView, UploadEncryptedFileView, DownloadEncryptedFileView, DeleteEncryptedFileView, UserLogsView
from django.contrib import admin

app_name = "vault"   

urlpatterns = [
    path('upload/', UploadEncryptedFileView.as_view(), name='upload_encrypted_file'),
    path('download/<int:pk>/', DownloadEncryptedFileView.as_view(), name='download_encrypted_file'),
    path('files/', EncryptedFileListView.as_view(), name='file-list'),
    path('delete/<int:pk>/', DeleteEncryptedFileView.as_view(), name='delete-encrypted-file'),
    path('logs/', UserLogsView.as_view(), name='user-logs'),    #es iqve sachveneblad 
    path('export/', ExportUserLogsView.as_view(), name='export-logs'),   # es chamosatvirtad
    path('admin/', admin.site.urls),
]
