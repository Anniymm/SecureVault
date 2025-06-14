from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import Enable2FASerializer, QRCodeResponseSerializer
from .utils import generate_otp_secret, get_qr_code_image
import pyotp
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


class Generate2FASetupView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Generate QR code and secret for 2FA setup",
        responses={200: QRCodeResponseSerializer},
    )

    def get(self, request):
        user = request.user
        settings = user.twofactorsettings

        if not settings.otp_secret:
            settings.otp_secret = generate_otp_secret()
            settings.save()

        qr_image = get_qr_code_image(settings.otp_secret, user.username)
        return Response({"qr_code": qr_image, "otp_secret": settings.otp_secret})


class Enable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Enable 2FA after verifying OTP",
        request=Enable2FASerializer,
        responses={200: OpenApiResponse(description="2FA enabled successfully.")},
    )

    def post(self, request):
        serializer = Enable2FASerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        settings = user.twofactorsettings
        settings.is_enabled = True
        settings.save()
        return Response({"detail": "2FA enabled successfully."})


class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Verify the 2FA OTP code",
        request=Enable2FASerializer,
        responses={
            200: OpenApiResponse(description="2FA verification successful."),
            400: OpenApiResponse(description="Invalid OTP or 2FA not enabled.")
        },
    )
    
    def post(self, request):
        code = request.data.get("otp_code")
        user = request.user
        settings = user.twofactorsettings

        if not settings.is_enabled or not settings.otp_secret:
            return Response({"detail": "2FA is not enabled for this user."}, status=400)

        totp = pyotp.TOTP(settings.otp_secret)
        if totp.verify(code):
            return Response({"detail": "2FA verification successful."})
        return Response({"detail": "Invalid OTP code."}, status=400)
