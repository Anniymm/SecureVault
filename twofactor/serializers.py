from rest_framework import serializers
from .models import TwoFactorSettings
import pyotp

class Enable2FASerializer(serializers.Serializer):
    otp_code = serializers.CharField()

    def validate_otp_code(self, code):
        user = self.context['request'].user
        secret = user.twofactorsettings.otp_secret
        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise serializers.ValidationError("Invalid OTP code.")
        return code
