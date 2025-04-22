from django.utils import timezone
from django.db import models
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from datetime import datetime, timedelta

from barberian.common.models import (
    User, Schedule, Appointment, Service
)
from barberian.notification.models import Notification
from barberian.common.serializers import (
    ScheduleSerializer, AppointmentSerializer,
    ServiceSerializer, UserSerializer
)
from barberian.notification.serializers import NotificationSerializer
from barberian.utils.permissions import IsStaff
from barberian.notification.utils import (
    notify_appointment_created,
    notify_appointment_updated,
    notify_appointment_canceled
)
from .models import StaffSettings
from .serializers import StaffSettingsSerializer, ChangePasswordSerializer, StaffProfileUpdateSerializer


# Schedule Management Views
class StaffScheduleListView(generics.ListAPIView):
    """
    API endpoint for staff to list their schedules.
    """
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user

        # Get date filters from query params
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = Schedule.objects.filter(staff=user).order_by('date', 'start_time')

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date_obj)
            except ValueError:
                pass

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date_obj)
            except ValueError:
                pass

        return queryset


class StaffScheduleCreateView(APIView):
    """
    API endpoint for staff to create a new schedule.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def post(self, request):
        # Extract data from request
        date_str = request.data.get('date')
        start_time_str = request.data.get('start_time')
        end_time_str = request.data.get('end_time')
        is_available = request.data.get('is_available', True)

        # Validate required fields
        if not date_str or not start_time_str or not end_time_str:
            return Response({
                "error": "Date, start time, and end time are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse date and times
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            # Validate times
            if start_time >= end_time:
                return Response({
                    "error": "Start time must be before end time."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check for overlapping schedules
            overlapping_schedule = Schedule.objects.filter(
                staff=request.user,
                date=date,
            ).filter(
                (models.Q(start_time__lt=end_time) & models.Q(end_time__gt=start_time))
            ).exists()

            if overlapping_schedule:
                return Response({
                    "error": "This schedule overlaps with an existing schedule."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create the schedule
            schedule = Schedule.objects.create(
                staff=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                is_available=is_available
            )

            return Response({
                "message": "Schedule created successfully.",
                "schedule": ScheduleSerializer(schedule).data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StaffScheduleDetailView(generics.RetrieveAPIView):
    """
    API endpoint for staff to retrieve details of a specific schedule.
    """
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.filter(staff=user)


class StaffScheduleUpdateView(generics.UpdateAPIView):
    """
    API endpoint for staff to update their schedule.
    """
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.filter(staff=user)


class StaffScheduleDeleteView(generics.DestroyAPIView):
    """
    API endpoint for staff to delete their schedule.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.filter(staff=user)


# Appointment Management Views
class StaffAppointmentListView(generics.ListAPIView):
    """
    API endpoint for staff to list their appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(staff=user).order_by('-start_time')

        # Filter by status if provided
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


class StaffTodayAppointmentsView(generics.ListAPIView):
    """
    API endpoint for staff to list their appointments for today.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()

        return Appointment.objects.filter(
            staff=user,
            start_time__date=today
        ).order_by('start_time')


class StaffUpcomingAppointmentsView(generics.ListAPIView):
    """
    API endpoint for staff to list their upcoming appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        return Appointment.objects.filter(
            staff=user,
            start_time__gt=now,
            status__in=['pending', 'confirmed']
        ).order_by('start_time')


class StaffAppointmentDetailView(generics.RetrieveAPIView):
    """
    API endpoint for staff to retrieve details of a specific appointment.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(staff=user)


class AppointmentStatusUpdateView(APIView):
    """
    API endpoint for staff to update the status of an appointment.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def post(self, request, pk):
        try:
            # Get the appointment
            appointment = Appointment.objects.get(pk=pk, staff=request.user)

            # Extract new status from request
            new_status = request.data.get('status')
            if not new_status:
                return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate status
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no_show']
            if new_status not in valid_statuses:
                return Response({
                    "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update appointment status
            appointment.status = new_status
            appointment.save()

            # Send notifications
            if new_status == 'cancelled':
                notify_appointment_canceled(appointment)
            else:
                notify_appointment_updated(appointment, appointment.start_time)

            return Response({
                "message": f"Appointment status updated to {new_status}.",
                "appointment": AppointmentSerializer(appointment).data
            }, status=status.HTTP_200_OK)

        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Service Browsing Views
class StaffServicesView(generics.ListAPIView):
    """
    API endpoint for staff to view available services.
    """
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]
    queryset = Service.objects.filter(is_active=True).order_by('category', 'name')


# Authentication Views
class StaffLoginView(APIView):
    """
    API endpoint for staff login.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user and user.role == 'staff':
            # Check if staff account is active
            if not user.is_active:
                return Response({
                    "error": "Your account is not active. Please contact the administrator."
                }, status=status.HTTP_403_FORBIDDEN)

            refresh = RefreshToken.for_user(user)

            # Log the login action
            if hasattr(request, 'META'):
                ip_address = request.META.get('REMOTE_ADDR')
            else:
                ip_address = None

            # Create or update staff settings if they don't exist
            StaffSettings.objects.get_or_create(staff=user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({
            "error": "Invalid credentials or not a staff member"
        }, status=status.HTTP_401_UNAUTHORIZED)


# Profile Management Views
class StaffProfileView(APIView):
    """
    API endpoint for staff to view their profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data

        # Get staff settings
        staff_settings, created = StaffSettings.objects.get_or_create(staff=user)
        settings_data = StaffSettingsSerializer(staff_settings).data

        # Combine user and settings data
        response_data = {
            "profile": user_data,
            "settings": settings_data
        }

        return Response(response_data)


class StaffProfileUpdateView(APIView):
    """
    API endpoint for staff to update their profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def put(self, request):
        user = request.user
        serializer = StaffProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": UserSerializer(user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffChangePasswordView(APIView):
    """
    API endpoint for staff to change their password.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    "old_password": ["Wrong password."]
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Update session to prevent logout
            update_session_auth_hash(request, user)

            return Response({
                "message": "Password updated successfully"
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffSettingsUpdateView(APIView):
    """
    API endpoint for staff to update their settings.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get(self, request):
        staff_settings, created = StaffSettings.objects.get_or_create(staff=request.user)
        serializer = StaffSettingsSerializer(staff_settings)
        return Response(serializer.data)

    def put(self, request):
        staff_settings, created = StaffSettings.objects.get_or_create(staff=request.user)
        serializer = StaffSettingsSerializer(staff_settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Settings updated successfully",
                "settings": serializer.data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffAvailabilityToggleView(APIView):
    """
    API endpoint for staff to toggle their overall availability.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def post(self, request):
        # Get date from request
        date_str = request.data.get('date')
        is_available = request.data.get('is_available')

        if is_available is None:
            return Response({"error": "Availability status is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            is_available_bool = bool(is_available)

            if date_str:
                # Toggle availability for specific date
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

                # Update or create schedule for this date
                schedule, created = Schedule.objects.get_or_create(
                    staff=request.user,
                    date=date,
                    defaults={
                        'start_time': datetime.strptime('09:00', '%H:%M').time(),
                        'end_time': datetime.strptime('17:00', '%H:%M').time(),
                        'is_available': is_available_bool
                    }
                )

                if not created:
                    schedule.is_available = is_available_bool
                    schedule.save()

                return Response({
                    "message": f"Availability for {date_str} set to {is_available_bool}",
                    "schedule": ScheduleSerializer(schedule).data
                })
            else:
                # Toggle availability for all future dates
                today = timezone.now().date()
                schedules = Schedule.objects.filter(
                    staff=request.user,
                    date__gte=today
                )

                # Update all schedules
                updated_count = schedules.update(is_available=is_available_bool)

                return Response({
                    "message": f"Updated availability for {updated_count} future dates",
                    "is_available": is_available_bool
                })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Notification Management Views
class StaffNotificationListView(generics.ListAPIView):
    """
    API endpoint for staff to list their notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user).order_by('-created_at')

        # Filter by read status if provided
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)

        return queryset
