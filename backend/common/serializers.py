from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Category, Service, Appointment, ServiceMedia,
    BusinessHours, Holiday, BusinessSettings, Schedule
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'bio', 'profile_image',
            'specialization', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'password2', 'first_name',
            'last_name', 'role', 'phone_number', 'is_active'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        # Check if password and password2 are provided
        if 'password' not in attrs or 'password2' not in attrs:
            raise serializers.ValidationError({"password": "Both password and password confirmation are required."})

        # Check if passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})

        # Ensure role is valid
        if 'role' in attrs and attrs['role'] not in ['admin', 'staff', 'client']:
            raise serializers.ValidationError({"role": "Role must be one of: admin, staff, client."})

        # Print validation data for debugging
        print(f"Validating user creation data: {attrs}")

        return attrs

    def create(self, validated_data):
        # Remove password2 field
        validated_data.pop('password2')

        # Print the validated data for debugging
        print(f"Creating user with data: {validated_data}")

        # Ensure role is set
        if 'role' not in validated_data:
            validated_data['role'] = 'client'  # Default to client if not specified

        user = User.objects.create_user(**validated_data)
        return user

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ServiceMediaSerializer(serializers.ModelSerializer):
    """
    Serializer for the ServiceMedia model
    """
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceMedia
        fields = ['id', 'file', 'file_url', 'file_type', 'is_primary']
        read_only_fields = ['id']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Service model
    """
    category_name = serializers.SerializerMethodField()
    media = ServiceMediaSerializer(many=True, read_only=True)
    primary_media = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'price', 'duration',
            'category', 'category_name', 'is_active', 'created_at', 'updated_at',
            'media', 'primary_media'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'media', 'primary_media']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_primary_media(self, obj):
        primary = obj.media.filter(is_primary=True).first()
        if primary:
            return ServiceMediaSerializer(primary, context=self.context).data
        # If no primary, return the first media item if any exist
        first_media = obj.media.first()
        if first_media:
            return ServiceMediaSerializer(first_media, context=self.context).data
        return None

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model
    """
    client_details = UserSerializer(source='client', read_only=True)
    staff_details = UserSerializer(source='staff', read_only=True)
    service_details = ServiceSerializer(source='service', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_details', 'staff', 'staff_details',
            'service', 'service_details', 'start_time', 'end_time',
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'end_time']

    def create(self, validated_data):
        appointment = Appointment(**validated_data)
        # Let the model's save method calculate the end_time
        appointment.save()
        return appointment

class BusinessHoursSerializer(serializers.ModelSerializer):
    """
    Serializer for the BusinessHours model
    """
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = BusinessHours
        fields = ['id', 'day_of_week', 'day_name', 'is_open', 'opening_time', 'closing_time']
        read_only_fields = ['id']

    def get_day_name(self, obj):
        return obj.get_day_of_week_display()

class HolidaySerializer(serializers.ModelSerializer):
    """
    Serializer for the Holiday model
    """
    class Meta:
        model = Holiday
        fields = ['id', 'name', 'date', 'is_recurring']
        read_only_fields = ['id']

class BusinessSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the BusinessSettings model
    """
    class Meta:
        model = BusinessSettings
        fields = [
            'id', 'business_name', 'address', 'phone', 'email',
            'logo_url', 'about', 'facebook_url', 'instagram_url',
            'twitter_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Schedule model
    """
    staff_details = UserSerializer(source='staff', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'staff', 'staff_details', 'date', 'start_time',
            'end_time', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class StaffAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for staff availability response
    """
    available = serializers.BooleanField()
    staff_name = serializers.CharField()
    date = serializers.DateField()
    message = serializers.CharField(required=False, allow_null=True)
    slots = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=True
        ),
        required=False
    )