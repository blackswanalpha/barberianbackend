from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Barber, Service, Appointment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class BarberSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Barber
        fields = ['id', 'user', 'phone_number', 'bio', 'profile_image', 'years_of_experience']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        barber = Barber.objects.create(user=user, **validated_data)
        return barber

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'duration_minutes', 'image']
        read_only_fields = ['id']

class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    barber_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'barber', 'barber_name', 
            'service', 'service_name', 'date', 'start_time', 'end_time', 
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username
    
    def get_barber_name(self, obj):
        return str(obj.barber)
    
    def get_service_name(self, obj):
        return obj.service.name
