from django.utils import timezone
from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from barberian.common.models import User, Service, Category, Appointment, BusinessHours, Holiday, BusinessSettings
from barberian.common.serializers import (
    ServiceSerializer, CategorySerializer, UserSerializer,
    AppointmentSerializer, StaffAvailabilitySerializer, BusinessSettingsSerializer
)
from barberian.utils.permissions import IsClient
from barberian.notification.utils import notify_appointment_created, notify_appointment_canceled, notify_appointment_updated
from barberian.client.models import ClientProfile, ClientPreference
from barberian.client.serializers import ClientProfileSerializer, ClientPreferenceSerializer

class ServiceListView(generics.ListAPIView):
    """
    API endpoint for listing services available for booking
    """
    queryset = Service.objects.all().order_by('category', 'name')
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Optional category filter
        category_id = self.request.query_params.get('category', None)
        if category_id:
            return Service.objects.filter(category_id=category_id).order_by('name')
        return Service.objects.all().order_by('category', 'name')

class ServiceDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving service details
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class CategoryListView(generics.ListAPIView):
    """
    API endpoint for listing service categories
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class StaffListView(generics.ListAPIView):
    """
    API endpoint for listing staff members available for appointments
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Return only active staff members
        return User.objects.filter(role='staff', is_active=True).order_by('first_name')

class StaffDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving staff details
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.filter(role='staff', is_active=True)

class StaffAvailabilityView(APIView):
    """
    API endpoint for checking staff availability for a specific date
    """
    permission_classes = [AllowAny]
    def get(self, request, pk):
        # Get the staff member
        try:
            staff = User.objects.get(pk=pk, role='staff', is_active=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Staff member not found or not available"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the date parameter from the request
        date_str = request.query_params.get('date', None)
        if not date_str:
            return Response(
                {"error": "Date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert to datetime.date object
            date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the date is a holiday
        if Holiday.objects.filter(date=date).exists():
            return Response({
                "available": False,
                "staff_name": f"{staff.first_name} {staff.last_name}",
                "date": date_str,
                "message": "The shop is closed for a holiday on this date",
                "slots": []
            })

        # Check business hours for the day of the week
        day_of_week = date.weekday()  # 0-6 (Monday-Sunday)
        try:
            business_hours = BusinessHours.objects.get(day_of_week=day_of_week)
            if not business_hours.is_open:
                return Response({
                    "available": False,
                    "staff_name": f"{staff.first_name} {staff.last_name}",
                    "date": date_str,
                    "message": f"The shop is closed on {business_hours.get_day_of_week_display()}",
                    "slots": []
                })
        except BusinessHours.DoesNotExist:
            return Response({
                "available": False,
                "staff_name": f"{staff.first_name} {staff.last_name}",
                "date": date_str,
                "message": "Business hours not configured for this day",
                "slots": []
            })

        # Get existing appointments for this staff member on this date
        start_of_day = timezone.datetime.combine(date, timezone.datetime.min.time())
        end_of_day = timezone.datetime.combine(date, timezone.datetime.max.time())

        existing_appointments = Appointment.objects.filter(
            staff=staff,
            start_time__date=date,
            status__in=['confirmed', 'pending']
        )

        # Calculate available time slots
        opening_time = business_hours.opening_time
        closing_time = business_hours.closing_time

        # Generate 30-minute time slots within business hours
        all_slots = []
        current_slot = opening_time

        while current_slot < closing_time:
            slot_end = (
                timezone.datetime.combine(timezone.datetime.today(), current_slot) +
                timezone.timedelta(minutes=30)
            ).time()

            if slot_end <= closing_time:
                all_slots.append({
                    "start": current_slot.strftime('%H:%M'),
                    "end": slot_end.strftime('%H:%M')
                })

            current_slot = slot_end

        # Remove slots that overlap with existing appointments
        available_slots = []
        for slot in all_slots:
            slot_start_time = timezone.datetime.strptime(slot['start'], '%H:%M').time()
            slot_end_time = timezone.datetime.strptime(slot['end'], '%H:%M').time()

            is_available = True
            for appointment in existing_appointments:
                appt_start = appointment.start_time.time()
                appt_end = appointment.end_time.time()

                # Check if this slot overlaps with the appointment
                if (
                    (slot_start_time < appt_end and slot_end_time > appt_start) or
                    (slot_start_time == appt_start and slot_end_time == appt_end)
                ):
                    is_available = False
                    break

            if is_available:
                available_slots.append(slot)

        return Response({
            "available": len(available_slots) > 0,
            "staff_name": f"{staff.first_name} {staff.last_name}",
            "date": date_str,
            "slots": available_slots
        })

class ClientAppointmentListView(generics.ListAPIView):
    """
    API endpoint for listing a client's appointments
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        # Return only the logged-in client's appointments
        return Appointment.objects.filter(
            client=self.request.user
        ).order_by('-start_time')

class ClientAppointmentDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a client's appointment details
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        # Return only the logged-in client's appointments
        return Appointment.objects.filter(client=self.request.user)

class ClientAppointmentCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a new appointment
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        # Set the client to the current user
        appointment = serializer.save(client=self.request.user, status='confirmed')

        # Send confirmation notification
        notify_appointment_created(appointment)

        return appointment


class BookingView(APIView):
    """
    API endpoint for the booking process
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from barberian.client.serializers import BookingSerializer
        from django.contrib.auth import get_user_model
        from datetime import datetime, timedelta

        User = get_user_model()

        # Initialize serializer with request context
        serializer = BookingSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            data = serializer.validated_data

            # Get service
            service = Service.objects.get(pk=data['service'])

            # Randomly select an available staff member
            import random
            available_staff = User.objects.filter(role='staff', is_active=True)

            if not available_staff.exists():
                return Response(
                    {"error": "No staff members are available for booking"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Select a random staff member
            staff = random.choice(list(available_staff))

            # Parse time slot
            time_slot = data['time_slot']
            start_time, end_time = time_slot.split('-')
            start_hour, start_minute = map(int, start_time.split(':'))

            # Create appointment start time
            appointment_date = data['date']
            appointment_start = timezone.make_aware(
                datetime.combine(appointment_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
            )

            # Handle guest booking
            if not request.user.is_authenticated:
                # Check if user already exists
                try:
                    client = User.objects.get(email=data['email'])
                except User.DoesNotExist:
                    # Create new user
                    import random
                    import string

                    # Generate a random password
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

                    # Create user
                    client = User.objects.create_user(
                        email=data['email'],
                        password=password,
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        phone_number=data['phone_number'],
                        role='client',
                        is_active=True
                    )

                    # Create client profile and preferences
                    from barberian.client.models import ClientProfile, ClientPreference
                    ClientProfile.objects.create(user=client)
                    ClientPreference.objects.create(
                        client=client,
                        email_notifications=True,
                        sms_notifications=True
                    )
            else:
                client = request.user

            # Create appointment
            appointment = Appointment.objects.create(
                client=client,
                staff=staff,
                service=service,
                start_time=appointment_start,
                status='confirmed',
                notes=data.get('notes', '')
            )

            # Send confirmation notification
            notify_appointment_created(appointment)

            # Return appointment details
            return Response({
                'message': 'Appointment booked successfully',
                'appointment': AppointmentSerializer(appointment).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientAppointmentCancelView(APIView):
    """
    API endpoint for cancelling a client's appointment
    """
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request, pk):
        try:
            # Get the appointment and ensure it belongs to the current user
            appointment = Appointment.objects.get(pk=pk, client=request.user)

            # Check if the appointment is already cancelled or completed
            if appointment.status in ['cancelled', 'completed']:
                return Response(
                    {"error": f"Cannot cancel an appointment with status '{appointment.status}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the appointment start time is in the past
            if appointment.start_time < timezone.now():
                return Response(
                    {"error": "Cannot cancel an appointment that has already started"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cancel the appointment
            appointment.status = 'cancelled'
            appointment.save()

            # Send cancellation notification
            notify_appointment_canceled(appointment)

            return Response(
                {"message": "Appointment successfully cancelled"},
                status=status.HTTP_200_OK
            )

        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found or does not belong to you"},
                status=status.HTTP_404_NOT_FOUND
            )


class ClientProfileView(APIView):
    """
    API endpoint for managing client profile
    """
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        # Get user profile
        user = request.user
        user_data = UserSerializer(user).data

        # Get or create client profile
        profile, created = ClientProfile.objects.get_or_create(user=user)
        profile_data = ClientProfileSerializer(profile).data

        # Get or create client preferences
        preferences, created = ClientPreference.objects.get_or_create(client=user)
        preferences_data = ClientPreferenceSerializer(preferences).data

        # Combine data
        response_data = {
            'user': user_data,
            'profile': profile_data,
            'preferences': preferences_data
        }

        return Response(response_data)

    def put(self, request):
        user = request.user

        # Update user data
        user_serializer = UserSerializer(user, data=request.data.get('user', {}), partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update profile data
        profile, created = ClientProfile.objects.get_or_create(user=user)
        profile_serializer = ClientProfileSerializer(profile, data=request.data.get('profile', {}), partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update preferences data
        preferences, created = ClientPreference.objects.get_or_create(client=user)
        preferences_serializer = ClientPreferenceSerializer(preferences, data=request.data.get('preferences', {}), partial=True)
        if preferences_serializer.is_valid():
            preferences_serializer.save()
        else:
            return Response(preferences_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Return updated data
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data,
            'profile': ClientProfileSerializer(profile).data,
            'preferences': ClientPreferenceSerializer(preferences).data
        })


class BusinessInfoView(APIView):
    """
    API endpoint for retrieving business information
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Get business settings
        try:
            settings = BusinessSettings.objects.get(pk=1)
            settings_data = BusinessSettingsSerializer(settings).data
        except BusinessSettings.DoesNotExist:
            settings_data = {}

        # Get business hours
        hours = BusinessHours.objects.all().order_by('day_of_week')
        hours_data = []
        for day in range(7):
            try:
                day_hours = hours.get(day_of_week=day)
                hours_data.append({
                    'day': day,
                    'day_name': day_hours.get_day_of_week_display(),
                    'is_open': day_hours.is_open,
                    'opening_time': day_hours.opening_time.strftime('%H:%M') if day_hours.is_open else None,
                    'closing_time': day_hours.closing_time.strftime('%H:%M') if day_hours.is_open else None
                })
            except BusinessHours.DoesNotExist:
                hours_data.append({
                    'day': day,
                    'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day],
                    'is_open': False,
                    'opening_time': None,
                    'closing_time': None
                })

        # Get upcoming holidays
        today = timezone.now().date()
        holidays = Holiday.objects.filter(Q(date__gte=today) | Q(is_recurring=True)).order_by('date')[:10]
        holidays_data = []
        for holiday in holidays:
            # For recurring holidays, adjust the year to current or next year
            if holiday.is_recurring and holiday.date < today:
                # If the holiday has already passed this year, show it for next year
                holiday_date = holiday.date.replace(year=today.year + 1)
            else:
                holiday_date = holiday.date

            holidays_data.append({
                'name': holiday.name,
                'date': holiday_date,
                'is_recurring': holiday.is_recurring
            })

        return Response({
            'business': settings_data,
            'hours': hours_data,
            'holidays': holidays_data
        })