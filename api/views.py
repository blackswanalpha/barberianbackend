from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Barber, Service, Appointment
from .serializers import UserSerializer, BarberSerializer, ServiceSerializer, AppointmentSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class BarberViewSet(viewsets.ModelViewSet):
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'bio']
    ordering_fields = ['user__first_name', 'years_of_experience']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'duration_minutes']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client__username', 'barber__user__username', 'service__name', 'status']
    ordering_fields = ['date', 'start_time', 'created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        # Admin can see all appointments
        if user.is_staff:
            return Appointment.objects.all()
        # Barbers can see their own appointments
        try:
            barber = Barber.objects.get(user=user)
            return Appointment.objects.filter(barber=barber)
        except Barber.DoesNotExist:
            # Regular users can only see their own appointments
            return Appointment.objects.filter(client=user)

    def perform_create(self, serializer):
        # If no client is specified, use the current user
        if 'client' not in serializer.validated_data:
            serializer.save(client=self.request.user)
        else:
            serializer.save()
