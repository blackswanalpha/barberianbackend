from rest_framework import serializers
from barberian.admin.models import UserLog, Report, MediaFile
from barberian.common.models import ServiceMedia, User

class UserLogSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = UserLog
        fields = ['id', 'user', 'user_email', 'action', 'details', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

class ServiceMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceMedia
        fields = ['id', 'service', 'file', 'file_type', 'is_primary', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class StaffSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'bio', 'profile_image', 'specialization',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data, role='staff')
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ReportSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'parameters',
            'created_by', 'created_by_name', 'created_at', 'updated_at', 'is_favorite'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None

class MediaFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = [
            'id', 'title', 'description', 'file', 'file_url', 'media_type',
            'uploaded_by', 'uploaded_by_name', 'created_at', 'updated_at', 'tags'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'file_url']

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else None

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
