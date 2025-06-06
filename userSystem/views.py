from rest_framework import generics
from .models import CustomUser
from .serializers import LogoutSerializer, RegisterSerializer, LoginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # user = serializer.validated_data['user']
            access = serializer.validated_data['access']
            refresh = serializer.validated_data['refresh']

            return Response({
                # "user": {
                #     "id": user.id,
                #     "username": user.username,
                #     "email": user.email,
                #     "first_name": user.first_name,
                #     "last_name": user.last_name,
                # },
                "access": access,
                "refresh": refresh
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.core.mail import send_mail
# from django.conf import settings
# from .serializers import PasswordResetConfirmSerializer
# from django.contrib.auth import get_user_model
# User = get_user_model()

# class PasswordResetRequestView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         user = User.objects.filter(email=email).first()
#         if user:
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             token = PasswordResetTokenGenerator().make_token(user)
#             reset_url = f"https://frontend.com/reset-password-confirm/{uid}/{token}/"

#             send_mail(
#                 subject="Password Reset Request",
#                 message=f"Click the link to reset your password: {reset_url}",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#             )
#         # Always return 200 to avoid leaking user existence info
#         return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


# class PasswordResetConfirmView(APIView):
#     def post(self, request):
#         serializer = PasswordResetConfirmSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 uid = urlsafe_base64_decode(serializer.validated_data['uidb64']).decode('utf-8')
#             except (TypeError, ValueError, OverflowError):
#                 return Response({"error": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)

#             token = serializer.validated_data['token']
#             new_password = serializer.validated_data['new_password']

#             user = User.objects.filter(pk=uid).first()
#             if user and PasswordResetTokenGenerator().check_token(user, token):
#                 user.set_password(new_password)
#                 user.save()
#                 return Response({"message": "Password reset successful."})
#             return Response({"error": "Invalid token or user ID."}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)