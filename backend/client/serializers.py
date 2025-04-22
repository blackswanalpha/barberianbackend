from rest_framework import serializers
from django.contrib.auth import get_user_model

from barberian.client.models import ClientProfile, ClientPreference
from barberian.common.serializers import UserSerializer, ServiceSerializer

User = get_user_model()

class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientProfile model
    """
    user_details = UserSerializer(source='user', read_only=True)
    preferred_staff_details = UserSerializer(source='preferred_staff', many=True, read_only=True)
    preferred_services_details = ServiceSerializer(source='preferred_services', many=True, read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'user_details', 'preferred_staff', 'preferred_staff_details',
            'preferred_services', 'preferred_services_details'
        ]
        read_only_fields = ['id', 'user']

class ClientPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientPreference model
    """
    client_details = UserSerializer(source='client', read_only=True)

    class Meta:
        model = ClientPreference
        fields = [
            'id', 'client', 'client_details', 'email_notifications',
            'sms_notifications', 'reminder_time'
        ]
        read_only_fields = ['id', 'client']

class BookingSerializer(serializers.Serializer):
    """
    Serializer for the booking process
    """
    service = serializers.IntegerField(required=True)
    # staff field is no longer required - will be chosen randomly
    date = serializers.DateField(required=True)
    time_slot = serializers.CharField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    # For guest bookings
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)

    def validate(self, data):
        """
        Validate the booking data
        """
        # Check if service exists
        try:
            from barberian.common.models import Service
            Service.objects.get(pk=data['service'], is_active=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError({"service": "Invalid service selected"})

        # Staff will be chosen randomly, so no need to validate staff

        # Check if the date is valid (not in the past)
        import datetime
        from django.utils import timezone

        if data['date'] < timezone.now().date():
            raise serializers.ValidationError({"date": "Cannot book appointments in the past"})

        # Check if the time slot is valid
        time_slot = data['time_slot']
        try:
            # We only need to validate the start time format
            start_time = time_slot.split('-')[0]
            start_hour, start_minute = map(int, start_time.split(':'))
        except (ValueError, IndexError):
            raise serializers.ValidationError({"time_slot": "Invalid time slot format. Use HH:MM-HH:MM"})

        # Create datetime objects for start and end times
        start_datetime = timezone.make_aware(
            datetime.datetime.combine(data['date'], datetime.time(start_hour, start_minute))
        )

        # Check if the appointment is in the future
        if start_datetime <= timezone.now():
            raise serializers.ValidationError({"time_slot": "Cannot book appointments in the past"})

        # For guest bookings, ensure all required fields are provided
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            for field in ['first_name', 'last_name', 'email', 'phone_number']:
                if field not in data or not data[field]:
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').title()} is required for guest bookings"})

        return data
