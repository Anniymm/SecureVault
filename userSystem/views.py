from django.conf import settings
from .serializers import LogoutSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, RegisterSerializer, LoginSerializer, TokenResponseSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model


class RegisterView(APIView):
    serializer_class = RegisterSerializer  # swaggeristvis minda es rom fieldebi visible gaxados 

    @extend_schema(
        request=serializer_class,
        responses={
            status.HTTP_201_CREATED: serializer_class,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Validation Error",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Validation Error Example",
                        value={
                            "email": ["Email is already registered.", "Enter a valid email address."],
                            "password": ["This password is too short. It must contain at least 8 characters."],
                        },
                    ),
                ],
            ),
        },
    )
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)  # Now using class attribute
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    serializer_class = LoginSerializer  
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Login successful", response=TokenResponseSerializer),
            400: OpenApiResponse(description="Invalid username or password.")
        }
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({
                "access": serializer.validated_data['access'],
                "refresh": serializer.validated_data['refresh']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    serializer_class = LogoutSerializer
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Successfully logged out."),
            400: OpenApiResponse(description="Given token not valid for any token type")
        }
    )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Successfully logged out."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



User = get_user_model()

class PasswordResetRequestView(APIView):
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Password reset link sent"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Validation Error",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Validation Error Example",
                        value={
                            "error": ["User not found"],
                            "email": [ "Enter a valid email address."]
                        },
                    ),
                ],
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:8000/reset-password-confirm/{uid}/{token}/"       # unda sheicvalos real domainit 

        send_mail(
            subject="Password Reset Link",
            message=f"Click the link to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({'message': 'Password reset link sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Password has been reset successfully."),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid/expired token or user ID",
                examples=[
                    OpenApiExample(
                        "Passwords don't match",
                        value={"non_field_errors": ["Passwords do not match"]},
                    ),
                    OpenApiExample(
                        "Invalid token",
                        value={"error": "Invalid or expired token"},
                    ),
                ],
            ),
        },
    )
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Invalid token or user ID'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'success': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)