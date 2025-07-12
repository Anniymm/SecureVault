from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_register_user_success(self):
        url = reverse("userSystem:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)

    def test_register_user_invalid_password(self):
        url = reverse("userSystem:register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "123",
            "confirm_password": "123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        url = reverse("userSystem:login")
        data = {
            "email": self.user.email,
            "password": "testpass123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_failure(self):
        url = reverse("userSystem:login")
        data = {
            "email": self.user.email,
            "password": "wrongpass"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_blacklists_token(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse("userSystem:logout")
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Successfully logged out.")

    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.user)
        url = reverse("userSystem:token_refresh")
        response = self.client.post(url, {"refresh": str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_password_reset_request_success(self):
        url = reverse("userSystem:password-reset")
        data = {"email": self.user.email}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password reset link sent")

    def test_password_reset_request_user_not_found(self):
        url = reverse("userSystem:password-reset")
        data = {"email": "unknown@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "User not found")

    def test_password_reset_confirm_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("userSystem:password-reset-confirm", args=[uid, token])
        data = {
            "password": "NewSecure123",
            "confirm_password": "NewSecure123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], "Password has been reset successfully.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecure123"))

    def test_password_reset_confirm_token_invalid(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("userSystem:password-reset-confirm", args=[uid, "invalidtoken"])
        data = {
            "password": "NewSecure123",
            "confirm_password": "NewSecure123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid or expired token")
