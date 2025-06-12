from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from tokenize import TokenError


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'display_name',
            'first_name', 'last_name',
            'password', 'confirm_password'
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'display_name': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """
        Check if the email already exists in the system.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


# RegisterView-stvis damwhirdes sheidzleba - ver movarge magram es amit unda shevcvalo samomavlod 
# class ValidationErrorSerializer(serializers.Serializer):
#     """
#     Serializer to represent validation errors returned by DRF.
#     simply passes the error dictionary as-is, preserving field names and messages.
#     """
#     def to_representation(self, instance):  #instanceshia errorebi
#         return instance
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        refresh = RefreshToken.for_user(user)
        return {
            # "user": user,   es jer ar vici minda tu ara, savaraudod ar minda ))))
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Invalid or expired refresh token.'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')


# class PasswordResetRequestSerializer(serializers.Serializer):
#     email = serializers.EmailField()

# class PasswordResetConfirmSerializer(serializers.Serializer):
#     uidb64 = serializers.CharField()
#     token = serializers.CharField()
#     new_password = serializers.CharField(min_length=8)

class TokenResponseSerializer(serializers.Serializer):  # es swaggeristvis mwhirdeba 
    access = serializers.CharField()
    refresh = serializers.CharField()
