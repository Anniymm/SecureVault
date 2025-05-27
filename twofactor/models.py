from django.db import models
from django.conf import settings

class TwoFactorSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=32, blank=True, null=True)
    last_verified = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"2FA settings for {self.user.username}"
