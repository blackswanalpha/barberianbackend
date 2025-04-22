from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Notification, NotificationPreference, SMSNotification
from barberian.common.serializers import UserSerializer

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """
    recipient_details = UserSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_details', 'title', 'message', 
            'is_read', 'notification_type', 'reference_id', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for the NotificationPreference model.
    """
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'user_details', 'notification_type', 
            'channel', 'is_enabled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SMSNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the SMSNotification model.
    """
    recipient_details = UserSerializer(source='recipient', read_only=True, required=False)
    
    class Meta:
        model = SMSNotification
        fields = [
            'id', 'recipient', 'recipient_details', 'phone_number', 
            'message', 'status', 'twilio_sid', 'notification_type', 
            'reference_id', 'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SMSManualSendSerializer(serializers.Serializer):
    """
    Serializer for manually sending an SMS.
    """
    phone_number = serializers.CharField(max_length=20)
    message = serializers.CharField()
    recipient_id = serializers.IntegerField(required=False)
    notification_type = serializers.ChoiceField(
        choices=SMSNotification.TYPE_CHOICES,
        default='manual'
    )
    reference_id = serializers.CharField(required=False, allow_blank=True)

class SMSStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating SMS status.
    """
    sms_id = serializers.IntegerField(required=False)
    max_age_hours = serializers.IntegerField(required=False, default=24)