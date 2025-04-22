from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Service, Category, BusinessSettings, BusinessHours
from .serializers import (
    ServiceSerializer, CategorySerializer, 
    BusinessSettingsSerializer, BusinessHoursSerializer
)
from barberian.utils.permissions import IsAdminOrReadOnly


class ServiceListView(generics.ListAPIView):
    """
    API endpoint that allows services to be viewed.
    """
    queryset = Service.objects.filter(active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_duration:
            queryset = queryset.filter(duration__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)
            
        return queryset


class ServiceDetailView(generics.RetrieveAPIView):
    """
    API endpoint that allows a service to be viewed.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class CategoryListView(generics.ListAPIView):
    """
    API endpoint that allows categories to be viewed.
    """
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    """
    API endpoint that allows a category to be viewed.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BusinessSettingsView(generics.RetrieveAPIView):
    """
    API endpoint that allows business settings to be viewed.
    """
    serializer_class = BusinessSettingsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        # Get or create business settings
        settings, created = BusinessSettings.objects.get_or_create(
            id=1,
            defaults={
                'business_name': 'Barberian',
                'address': '123 Main St, Anytown, USA',
                'phone_number': '555-123-4567',
                'email': 'contact@barberian.com',
                'website': 'www.barberian.com',
                'opening_time': '09:00:00',
                'closing_time': '18:00:00',
                'allow_client_cancellation': True,
                'cancellation_time_window': 24
            }
        )
        return settings


class BusinessHoursListView(generics.ListAPIView):
    """
    API endpoint that allows business hours to be viewed.
    """
    queryset = BusinessHours.objects.all().order_by('day_of_week')
    serializer_class = BusinessHoursSerializer
    permission_classes = [permissions.AllowAny]
