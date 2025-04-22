from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import StaffSettings
from barberian.common.serializers import UserSerializer

User = get_user_model()

class StaffSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the StaffSettings model
    """
    staff_details = UserSerializer(source='staff', read_only=True)
    
    class Meta:
        model = StaffSettings
        fields = [
            'id', 'staff', 'staff_details', 'notification_preference',
            'email_notifications', 'sms_notifications', 'auto_confirm_appointments',
            'calendar_view_preference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'staff', 'created_at', 'updated_at']

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, data):
        """
        Check that the old password is correct and the new passwords match
        """
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "The two password fields didn't match."})
        
        # Validate password strength
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return data

class StaffProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating staff profile
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'bio', 'profile_image', 'specialization']
        
    def validate_phone_number(self, value):
        """
        Validate phone number format
        """
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +1)")
        return value
