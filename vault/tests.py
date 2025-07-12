import os
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status
from cryptography.fernet import Fernet
from vault.models import EncryptedFile, UserLog
from django.contrib.auth import get_user_model

User = get_user_model()


class VaultViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass12345")
        self.client.login(username="testuser", password="pass12345")
        self.file = SimpleUploadedFile("test.txt", b"This is a test file.", content_type="text/plain")

    def test_upload_file_encrypted(self):
        url = reverse("vault:upload_encrypted_file")
        response = self.client.post(url, {"file": self.file, "note": "test note"}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EncryptedFile.objects.count(), 1)
        self.assertEqual(UserLog.objects.filter(action="UPLOAD").count(), 1)

    def test_download_encrypted_file(self):
        # Upload first
        upload_url = reverse("vault:upload_encrypted_file")
        upload_response = self.client.post(upload_url, {"file": self.file}, format="multipart")
        file_id = upload_response.data["id"]
        download_url = reverse("vault:download_encrypted_file", kwargs={"pk": file_id})

        response = self.client.get(download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Content-Disposition", response)

    def test_file_list(self):
        # Upload 2 files
        self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")
        self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")

        response = self.client.get(reverse("vault:file-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_file_list_filter_by_extension(self):
        self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")
        response = self.client.get(reverse("vault:file-list") + "?ext=txt")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_delete_encrypted_file(self):
        # Upload first
        upload = self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")
        file_id = upload.data["id"]
        path = EncryptedFile.objects.get(pk=file_id).file.path
        self.assertTrue(os.path.exists(path))

        url = reverse("vault:delete-encrypted-file", kwargs={"pk": file_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(os.path.exists(path))
        self.assertEqual(UserLog.objects.filter(action="DELETE").count(), 1)

    def test_user_logs_view(self):
        # Upload file to generate log
        self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")

        response = self.client.get(reverse("vault:user-logs"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_export_logs_json_file(self):
        # Generate a log
        self.client.post(reverse("vault:upload_encrypted_file"), {"file": self.file}, format="multipart")
        url = reverse("vault:export-logs")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("Content-Disposition", response)
