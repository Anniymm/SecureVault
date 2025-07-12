from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import pyotp
from .models import TwoFactorSettings 

User = get_user_model()

class TwoFactorAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.login(username="testuser", password="testpass123")

        self.settings = self.user.twofactorsettings

    def test_generate_2fa_setup_creates_secret_and_qr(self):
        url = reverse("generate-2fa")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("qr_code", response.data)
        self.assertIn("otp_secret", response.data)
        self.assertTrue(self.user.twofactorsettings.otp_secret)

    def test_enable_2fa_with_valid_otp(self):
        # Generate secret and OTP
        self.settings.otp_secret = pyotp.random_base32()
        self.settings.save()
        totp = pyotp.TOTP(self.settings.otp_secret)
        otp = totp.now()

        url = reverse("enable-2fa")
        response = self.client.post(url, {"otp_code": otp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.twofactorsettings.is_enabled)
        self.assertEqual(response.data["detail"], "2FA enabled successfully.")

    def test_enable_2fa_with_invalid_otp(self):
        self.settings.otp_secret = pyotp.random_base32()
        self.settings.save()

        url = reverse("enable-2fa")
        response = self.client.post(url, {"otp_code": "123456"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_2fa_with_correct_code(self):
        self.settings.otp_secret = pyotp.random_base32()
        self.settings.is_enabled = True
        self.settings.save()
        totp = pyotp.TOTP(self.settings.otp_secret)
        otp = totp.now()

        url = reverse("verify-2fa")
        response = self.client.post(url, {"otp_code": otp})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "2FA verification successful.")

    def test_verify_2fa_with_incorrect_code(self):
        self.settings.otp_secret = pyotp.random_base32()
        self.settings.is_enabled = True
        self.settings.save()

        url = reverse("verify-2fa")
        response = self.client.post(url, {"otp_code": "000000"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Invalid OTP code.")

    def test_verify_2fa_without_being_enabled(self):
        self.settings.otp_secret = pyotp.random_base32()
        self.settings.is_enabled = False
        self.settings.save()
        totp = pyotp.TOTP(self.settings.otp_secret)
        otp = totp.now()

        url = reverse("verify-2fa")
        response = self.client.post(url, {"otp_code": otp})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("2FA is not enabled", response.data["detail"])
