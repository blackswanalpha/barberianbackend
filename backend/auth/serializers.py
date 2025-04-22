from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from barberian.notification.models import NotificationPreference

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom TokenObtainPairSerializer that includes user's role and name
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role
        token['name'] = f"{user.first_name} {user.last_name}"
        token['email'] = user.email

        return token


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone_number', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Only allow client registration through public endpoint
        if self.context.get('request') and not self.context['request'].user.is_staff:
            if attrs.get('role') and attrs['role'] != 'client':
                raise serializers.ValidationError({"role": "You can only register as a client."})

        return attrs

    def create(self, validated_data):
        # Remove the password2 field from validated_data
        validated_data.pop('password2', None)

        # Check if role is passed and requestor is not staff
        if self.context.get('request') and not self.context['request'].user.is_staff:
            validated_data['role'] = 'client'

        user = User.objects.create_user(**validated_data)

        # Create notification preferences for the user
        NotificationPreference.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active')
        read_only_fields = ('id', 'is_active')


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value
