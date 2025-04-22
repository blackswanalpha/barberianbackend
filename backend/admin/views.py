from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from barberian.common.models import (
    User, Category, Service, Appointment, ServiceMedia,
    BusinessSettings, BusinessHours, Holiday
)
from barberian.notification.models import SMSNotification
from barberian.admin.models import UserLog, Report, MediaFile
from barberian.common.serializers import (
    UserSerializer, UserCreateSerializer, CategorySerializer, ServiceSerializer,
    AppointmentSerializer, BusinessSettingsSerializer,
    BusinessHoursSerializer, HolidaySerializer
)
from barberian.notification.serializers import SMSNotificationSerializer
from barberian.admin.serializers import (
    UserLogSerializer, ServiceMediaSerializer, StaffSerializer,
    ReportSerializer, MediaFileSerializer
)
from barberian.utils.permissions import IsAdmin
from barberian.notification.utils import (
    notify_appointment_created,
    notify_appointment_updated,
    notify_appointment_canceled
)


# User Management Views
class UserListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all users and creating a new user.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class UserActivateView(APIView):
    """
    API endpoint for activating a user.
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = True
            user.save()
            return Response({"message": f"User {user.email} has been activated."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class UserDeactivateView(APIView):
    """
    API endpoint for deactivating a user.
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user == request.user:
                return Response({"error": "You cannot deactivate yourself."}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = False
            user.save()
            return Response({"message": f"User {user.email} has been deactivated."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# Staff Management Views
class StaffListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return StaffSerializer

    def get_queryset(self):
        return User.objects.filter(role='staff')

    def perform_create(self, serializer):
        # Always set role to staff, regardless of what was sent in the request
        serializer.save(role='staff')

    def create(self, request, *args, **kwargs):
        # Log the request data for debugging
        print(f"Staff creation request data: {request.data}")
        return super().create(request, *args, **kwargs)


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.filter(role='staff')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserSerializer
        return StaffSerializer

    def perform_update(self, serializer):
        serializer.save(role='staff')


# Client Management Views
class ClientListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing all clients and creating new ones.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='client').order_by('-date_joined')

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)

        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        # Always set role to client, regardless of what was sent in the request
        serializer.save(role='client')

    def create(self, request, *args, **kwargs):
        # Log the request data for debugging
        print(f"Request data: {request.data}")
        return super().create(request, *args, **kwargs)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a client's details.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.filter(role='client')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserSerializer
        return UserSerializer

    def perform_update(self, serializer):
        serializer.save(role='client')

    def perform_destroy(self, instance):
        # Log the deletion
        UserLog.objects.create(
            user=self.request.user,
            action='delete_client',
            details=f'Deleted client: {instance.email}',
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        instance.delete()


# Category Management Views
class CategoryListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all categories and creating a new category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]


# Service Management Views
class ServiceListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all services and creating a new service.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdmin]


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a service.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdmin]


# Appointment Management Views
class AppointmentListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all appointments and creating new appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = Appointment.objects.all().order_by('-start_time')

        # Handle filtering
        status = self.request.query_params.get('status')
        client_id = self.request.query_params.get('client_id')
        staff_id = self.request.query_params.get('staff_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        start_time_after = self.request.query_params.get('start_time_after')
        start_time_before = self.request.query_params.get('start_time_before')

        if status:
            queryset = queryset.filter(status=status)
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        if staff_id:
            queryset = queryset.filter(staff_id=staff_id)
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        if start_time_after:
            queryset = queryset.filter(start_time__gte=start_time_after)
        if start_time_before:
            queryset = queryset.filter(start_time__lte=start_time_before)

        return queryset

    def perform_create(self, serializer):
        appointment = serializer.save()
        # Notify the client and staff about the new appointment
        notify_appointment_created(appointment)


class TodayAppointmentsView(generics.ListAPIView):
    """
    API endpoint for listing today's appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        today = timezone.now().date()
        return Appointment.objects.filter(
            start_time__date=today
        ).order_by('start_time')


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving or updating an appointment.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdmin]


class AppointmentCancelView(APIView):
    """
    API endpoint for cancelling an appointment.
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            appointment.status = 'cancelled'
            appointment.save()

            # Notify the client and staff about cancellation
            notify_appointment_canceled(appointment)

            return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)


# Business Settings Views
class BusinessSettingsView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving or updating business settings.
    """
    serializer_class = BusinessSettingsSerializer
    permission_classes = [IsAdmin]

    def get_object(self):
        # Get or create default business settings
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


# Business Hours Views
class BusinessHoursListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all business hours and creating new business hours.
    """
    queryset = BusinessHours.objects.all().order_by('day_of_week')
    serializer_class = BusinessHoursSerializer
    permission_classes = [IsAdmin]


class BusinessHoursUpdateView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving or updating business hours.
    """
    queryset = BusinessHours.objects.all()
    serializer_class = BusinessHoursSerializer
    permission_classes = [IsAdmin]


# Holiday Management Views
class HolidayListView(generics.ListCreateAPIView):
    """
    API endpoint for listing all holidays and creating a new holiday.
    """
    queryset = Holiday.objects.all().order_by('date')
    serializer_class = HolidaySerializer
    permission_classes = [IsAdmin]


class HolidayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating or deleting a holiday.
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    permission_classes = [IsAdmin]


# Admin Login View
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user and user.role == 'admin':
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'detail': 'Invalid credentials or not an admin'}, status=status.HTTP_401_UNAUTHORIZED)


# Reporting Views
class DashboardView(APIView):
    """
    API endpoint for retrieving dashboard statistics.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        start_of_month = datetime(today.year, today.month, 1).date()

        # Count statistics
        total_clients = User.objects.filter(role='client').count()
        total_staff = User.objects.filter(role='staff').count()
        total_services = Service.objects.count()

        # Appointment statistics
        total_appointments = Appointment.objects.count()
        today_appointments = Appointment.objects.filter(start_time__date=today).count()
        monthly_appointments = Appointment.objects.filter(start_time__date__gte=start_of_month).count()

        # Revenue statistics (assuming completed appointments)
        monthly_revenue = Appointment.objects.filter(
            status='completed',
            start_time__date__gte=start_of_month
        ).aggregate(
            total=Sum('service__price')
        )['total'] or 0

        # Status breakdown
        status_breakdown = Appointment.objects.values('status').annotate(count=Count('id'))

        return Response({
            'total_clients': total_clients,
            'total_staff': total_staff,
            'total_services': total_services,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'monthly_appointments': monthly_appointments,
            'monthly_revenue': float(monthly_revenue),
            'status_breakdown': status_breakdown
        })


class StaffPerformanceReportView(APIView):
    """
    API endpoint for retrieving staff performance report.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        # Get start and end date filters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get performance by staff
        staff_performance = []
        staff_members = User.objects.filter(role='staff')

        for staff in staff_members:
            # Get appointments data
            appointments = Appointment.objects.filter(
                staff=staff,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )

            total_appointments = appointments.count()
            if total_appointments == 0:
                continue

            completed_appointments = appointments.filter(status='completed').count()
            cancelled_appointments = appointments.filter(status='cancelled').count()
            no_show_appointments = appointments.filter(status='no_show').count()

            # Calculate revenue
            revenue = appointments.filter(status='completed').aggregate(
                total=Sum('service__price')
            )['total'] or 0

            # Calculate completion rate
            completion_rate = (completed_appointments / total_appointments) * 100 if total_appointments > 0 else 0

            staff_performance.append({
                'staff_id': staff.id,
                'staff_name': staff.get_full_name(),
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'cancelled_appointments': cancelled_appointments,
                'no_show_appointments': no_show_appointments,
                'revenue': float(revenue),
                'completion_rate': round(completion_rate, 2)
            })

        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'staff_performance': staff_performance
        })


class ServiceAnalysisReportView(APIView):
    """
    API endpoint for retrieving service analysis report.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        # Get start and end date filters
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get analysis by service
        service_analysis = []
        services = Service.objects.all()

        for service in services:
            # Get appointments data
            appointments = Appointment.objects.filter(
                service=service,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )

            total_appointments = appointments.count()
            if total_appointments == 0:
                continue

            completed_appointments = appointments.filter(status='completed').count()

            # Calculate revenue
            revenue = appointments.filter(status='completed').aggregate(
                total=Sum('service__price')
            )['total'] or 0

            # Calculate percentage of total bookings
            all_appointments = Appointment.objects.filter(
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            ).count()

            percentage = (total_appointments / all_appointments) * 100 if all_appointments > 0 else 0

            service_analysis.append({
                'service_id': service.id,
                'service_name': service.name,
                'category': service.category.name,
                'price': float(service.price),
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'revenue': float(revenue),
                'percentage_of_bookings': round(percentage, 2)
            })

        # Sort by total appointments
        service_analysis.sort(key=lambda x: x['total_appointments'], reverse=True)

        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'service_analysis': service_analysis
        })


class AppointmentMetricsReportView(APIView):
    """
    API endpoint for retrieving appointment metrics report.
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        # Get time period
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()

        if period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Start of week (Monday)
            title = f"Appointment Metrics for Week of {start_date.strftime('%Y-%m-%d')}"
            group_by = 'day'
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1).date()  # Start of month
            title = f"Appointment Metrics for {start_date.strftime('%B %Y')}"
            group_by = 'day'
        elif period == 'year':
            start_date = datetime(today.year, 1, 1).date()  # Start of year
            title = f"Appointment Metrics for {today.year}"
            group_by = 'month'
        else:
            return Response({"error": "Invalid period specified"}, status=status.HTTP_400_BAD_REQUEST)

        # Get appointments in the period
        appointments = Appointment.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=today
        )

        # Calculate metrics
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        no_show_appointments = appointments.filter(status='no_show').count()

        # Calculate completion rate
        completion_rate = (completed_appointments / total_appointments) * 100 if total_appointments > 0 else 0

        # Calculate revenue
        revenue = appointments.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0

        # Calculate average appointments per day
        days_count = (today - start_date).days + 1
        avg_appointments_per_day = total_appointments / days_count if days_count > 0 else 0

        # Get appointment distribution by time
        if group_by == 'day':
            # Group by day of week
            distribution = {}
            for i in range(7):
                day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
                count = appointments.filter(start_time__week_day=i+2).count()  # Django's week_day is 1-7 where 1=Sunday
                distribution[day_name] = count
        else:
            # Group by month
            distribution = {}
            for i in range(1, 13):
                month_name = datetime(2000, i, 1).strftime('%B')
                count = appointments.filter(start_time__month=i).count()
                distribution[month_name] = count

        return Response({
            'title': title,
            'period': period,
            'start_date': start_date,
            'end_date': today,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'no_show_appointments': no_show_appointments,
            'completion_rate': round(completion_rate, 2),
            'revenue': float(revenue),
            'avg_appointments_per_day': round(avg_appointments_per_day, 2),
            'distribution': distribution
        })


# User Log Management Views
class UserLogListView(generics.ListAPIView):
    serializer_class = UserLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = UserLog.objects.all()

        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        return queryset


class UserLogDeleteView(generics.DestroyAPIView):
    serializer_class = UserLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = UserLog.objects.all()


# SMS Notification Management Views
class SMSNotificationListView(generics.ListAPIView):
    """
    API endpoint for listing SMS notifications.
    """
    serializer_class = SMSNotificationSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = SMSNotification.objects.all().order_by('-created_at')

        # Handle filtering
        status = self.request.query_params.get('status')
        user_id = self.request.query_params.get('user_id')
        notification_type = self.request.query_params.get('notification_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(status=status)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset


class SMSNotificationDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving SMS notification details.
    """
    queryset = SMSNotification.objects.all()
    serializer_class = SMSNotificationSerializer
    permission_classes = [IsAdmin]


class SendSMSNotificationView(APIView):
    """
    API endpoint for sending SMS notifications manually from the admin panel.
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        user_id = request.data.get('user_id')

        if not phone_number:
            return Response(
                {"error": "Phone number is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not message:
            return Response(
                {"error": "Message content is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get user if user_id is provided
            user = None
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return Response(
                        {"error": f"User with ID {user_id} not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Send the SMS and log it in the database
            from barberian.notification.utils import send_sms_notification
            sms_notification = send_sms_notification(
                phone_number=phone_number,
                message=message,
                user=user,
                notification_type='manual'
            )

            if sms_notification and sms_notification.twilio_sid:
                # Serialize the notification data
                serializer = SMSNotificationSerializer(sms_notification)
                return Response({
                    "message": "SMS sent successfully.",
                    "sms_notification": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Failed to send SMS. Check Twilio credentials."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": f"Error sending SMS: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateSMSStatusView(APIView):
    """
    API endpoint for updating the status of SMS notifications.
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        try:
            # Call the bulk update function
            from barberian.notification.utils import update_sms_statuses
            results = update_sms_statuses(max_age_hours=24)

            return Response({
                "message": "SMS status update completed.",
                "updated": results['updated'],
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"Error updating SMS statuses: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Report Management Views
class ReportListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating reports.
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Report.objects.all()

        # Filter by report type
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        # Filter by favorite status
        is_favorite = self.request.query_params.get('is_favorite')
        if is_favorite is not None:
            is_favorite_bool = is_favorite.lower() == 'true'
            queryset = queryset.filter(is_favorite=is_favorite_bool)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a report.
    """
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Report.objects.all()


class ReportGenerateView(APIView):
    """
    API endpoint for generating a report based on parameters.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        report_type = request.data.get('report_type')
        parameters = request.data.get('parameters', {})
        save_report = request.data.get('save_report', False)
        report_name = request.data.get('name', f"{report_type.replace('_', ' ').title()} Report")

        if not report_type:
            return Response({"error": "Report type is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate report data based on type
        if report_type == 'staff_performance':
            data = self.generate_staff_performance_report(parameters)
        elif report_type == 'service_analysis':
            data = self.generate_service_analysis_report(parameters)
        elif report_type == 'appointment_metrics':
            data = self.generate_appointment_metrics_report(parameters)
        elif report_type == 'revenue':
            data = self.generate_revenue_report(parameters)
        elif report_type == 'client_activity':
            data = self.generate_client_activity_report(parameters)
        else:
            return Response({"error": "Invalid report type"}, status=status.HTTP_400_BAD_REQUEST)

        # Save report if requested
        if save_report:
            report = Report.objects.create(
                name=report_name,
                description=request.data.get('description', ''),
                report_type=report_type,
                parameters=parameters,
                created_by=request.user
            )
            return Response({
                "message": "Report generated and saved successfully",
                "report_id": report.id,
                "data": data
            })

        return Response(data)

    def generate_staff_performance_report(self, parameters):
        # Extract parameters
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date')
        staff_id = parameters.get('staff_id')

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get staff members
        if staff_id:
            staff_members = User.objects.filter(id=staff_id, role='staff')
        else:
            staff_members = User.objects.filter(role='staff')

        # Get performance by staff
        staff_performance = []
        for staff in staff_members:
            # Get appointments data
            appointments = Appointment.objects.filter(
                staff=staff,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )

            total_appointments = appointments.count()
            if total_appointments == 0:
                continue

            completed_appointments = appointments.filter(status='completed').count()
            cancelled_appointments = appointments.filter(status='cancelled').count()
            no_show_appointments = appointments.filter(status='no_show').count()

            # Calculate revenue
            revenue = appointments.filter(status='completed').aggregate(
                total=Sum('service__price')
            )['total'] or 0

            # Calculate completion rate
            completion_rate = (completed_appointments / total_appointments) * 100 if total_appointments > 0 else 0

            staff_performance.append({
                'staff_id': staff.id,
                'staff_name': staff.get_full_name(),
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'cancelled_appointments': cancelled_appointments,
                'no_show_appointments': no_show_appointments,
                'revenue': float(revenue),
                'completion_rate': round(completion_rate, 2)
            })

        return {
            'start_date': start_date,
            'end_date': end_date,
            'staff_performance': staff_performance
        }

    def generate_service_analysis_report(self, parameters):
        # Extract parameters
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date')
        category_id = parameters.get('category_id')

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get services
        if category_id:
            services = Service.objects.filter(category_id=category_id)
        else:
            services = Service.objects.all()

        # Get analysis by service
        service_analysis = []
        for service in services:
            # Get appointments data
            appointments = Appointment.objects.filter(
                service=service,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )

            total_appointments = appointments.count()
            if total_appointments == 0:
                continue

            completed_appointments = appointments.filter(status='completed').count()

            # Calculate revenue
            revenue = appointments.filter(status='completed').aggregate(
                total=Sum('service__price')
            )['total'] or 0

            # Calculate percentage of total bookings
            all_appointments = Appointment.objects.filter(
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            ).count()

            percentage = (total_appointments / all_appointments) * 100 if all_appointments > 0 else 0

            service_analysis.append({
                'service_id': service.id,
                'service_name': service.name,
                'category': service.category.name,
                'price': float(service.price),
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'revenue': float(revenue),
                'percentage_of_bookings': round(percentage, 2)
            })

        # Sort by total appointments
        service_analysis.sort(key=lambda x: x['total_appointments'], reverse=True)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'service_analysis': service_analysis
        }

    def generate_appointment_metrics_report(self, parameters):
        # Extract parameters
        period = parameters.get('period', 'month')

        today = timezone.now().date()

        if period == 'week':
            start_date = today - timedelta(days=today.weekday())  # Start of week (Monday)
            title = f"Appointment Metrics for Week of {start_date.strftime('%Y-%m-%d')}"
            group_by = 'day'
        elif period == 'month':
            start_date = datetime(today.year, today.month, 1).date()  # Start of month
            title = f"Appointment Metrics for {start_date.strftime('%B %Y')}"
            group_by = 'day'
        elif period == 'year':
            start_date = datetime(today.year, 1, 1).date()  # Start of year
            title = f"Appointment Metrics for {today.year}"
            group_by = 'month'
        else:
            return {"error": "Invalid period specified"}

        # Get appointments in the period
        appointments = Appointment.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=today
        )

        # Calculate metrics
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        no_show_appointments = appointments.filter(status='no_show').count()

        # Calculate completion rate
        completion_rate = (completed_appointments / total_appointments) * 100 if total_appointments > 0 else 0

        # Calculate revenue
        revenue = appointments.filter(status='completed').aggregate(
            total=Sum('service__price')
        )['total'] or 0

        # Calculate average appointments per day
        days_count = (today - start_date).days + 1
        avg_appointments_per_day = total_appointments / days_count if days_count > 0 else 0

        # Get appointment distribution by time
        if group_by == 'day':
            # Group by day of week
            distribution = {}
            for i in range(7):
                day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
                count = appointments.filter(start_time__week_day=i+2).count()  # Django's week_day is 1-7 where 1=Sunday
                distribution[day_name] = count
        else:
            # Group by month
            distribution = {}
            for i in range(1, 13):
                month_name = datetime(2000, i, 1).strftime('%B')
                count = appointments.filter(start_time__month=i).count()
                distribution[month_name] = count

        return {
            'title': title,
            'period': period,
            'start_date': start_date,
            'end_date': today,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'no_show_appointments': no_show_appointments,
            'completion_rate': round(completion_rate, 2),
            'revenue': float(revenue),
            'avg_appointments_per_day': round(avg_appointments_per_day, 2),
            'distribution': distribution
        }

    def generate_revenue_report(self, parameters):
        # Extract parameters
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date')
        group_by = parameters.get('group_by', 'day')  # day, week, month

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get completed appointments in the period
        appointments = Appointment.objects.filter(
            start_time__date__gte=start_date,
            start_time__date__lte=end_date,
            status='completed'
        )

        # Calculate total revenue
        total_revenue = appointments.aggregate(
            total=Sum('service__price')
        )['total'] or 0

        # Group revenue by time period
        revenue_data = []

        if group_by == 'day':
            # Group by day
            current_date = start_date
            while current_date <= end_date:
                day_revenue = appointments.filter(
                    start_time__date=current_date
                ).aggregate(
                    total=Sum('service__price')
                )['total'] or 0

                revenue_data.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'revenue': float(day_revenue)
                })

                current_date += timedelta(days=1)

        elif group_by == 'week':
            # Group by week
            # Start from the beginning of the week containing start_date
            week_start = start_date - timedelta(days=start_date.weekday())
            current_week_start = week_start

            while current_week_start <= end_date:
                current_week_end = current_week_start + timedelta(days=6)
                week_revenue = appointments.filter(
                    start_time__date__gte=current_week_start,
                    start_time__date__lte=min(current_week_end, end_date)
                ).aggregate(
                    total=Sum('service__price')
                )['total'] or 0

                revenue_data.append({
                    'week': f"{current_week_start.strftime('%Y-%m-%d')} to {min(current_week_end, end_date).strftime('%Y-%m-%d')}",
                    'revenue': float(week_revenue)
                })

                current_week_start += timedelta(days=7)

        elif group_by == 'month':
            # Group by month
            # Start from the beginning of the month containing start_date
            month_start = datetime(start_date.year, start_date.month, 1).date()
            current_month = month_start

            while current_month <= end_date:
                # Calculate the last day of the current month
                if current_month.month == 12:
                    next_month = datetime(current_month.year + 1, 1, 1).date()
                else:
                    next_month = datetime(current_month.year, current_month.month + 1, 1).date()

                month_end = next_month - timedelta(days=1)

                month_revenue = appointments.filter(
                    start_time__date__gte=current_month,
                    start_time__date__lte=min(month_end, end_date)
                ).aggregate(
                    total=Sum('service__price')
                )['total'] or 0

                revenue_data.append({
                    'month': current_month.strftime('%B %Y'),
                    'revenue': float(month_revenue)
                })

                # Move to the next month
                current_month = next_month

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': float(total_revenue),
            'group_by': group_by,
            'revenue_data': revenue_data
        }

    def generate_client_activity_report(self, parameters):
        # Extract parameters
        start_date_str = parameters.get('start_date')
        end_date_str = parameters.get('end_date')

        today = timezone.now().date()
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today - timedelta(days=30)
        else:
            start_date = today - timedelta(days=30)

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                end_date = today
        else:
            end_date = today

        # Get all clients
        clients = User.objects.filter(role='client')

        # Get client activity data
        client_activity = []

        for client in clients:
            # Get appointments in the period
            appointments = Appointment.objects.filter(
                client=client,
                start_time__date__gte=start_date,
                start_time__date__lte=end_date
            )

            total_appointments = appointments.count()
            if total_appointments == 0:
                continue

            completed_appointments = appointments.filter(status='completed').count()
            cancelled_appointments = appointments.filter(status='cancelled').count()
            no_show_appointments = appointments.filter(status='no_show').count()

            # Calculate total spent
            total_spent = appointments.filter(status='completed').aggregate(
                total=Sum('service__price')
            )['total'] or 0

            # Get most recent appointment
            most_recent = appointments.order_by('-start_time').first()

            # Get most used service
            service_counts = appointments.values('service__name').annotate(count=Count('service')).order_by('-count')
            most_used_service = service_counts[0]['service__name'] if service_counts else None

            client_activity.append({
                'client_id': client.id,
                'client_name': client.get_full_name(),
                'email': client.email,
                'phone_number': client.phone_number,
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'cancelled_appointments': cancelled_appointments,
                'no_show_appointments': no_show_appointments,
                'total_spent': float(total_spent),
                'last_appointment': most_recent.start_time if most_recent else None,
                'most_used_service': most_used_service
            })

        # Sort by total appointments
        client_activity.sort(key=lambda x: x['total_appointments'], reverse=True)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_clients': len(client_activity),
            'client_activity': client_activity
        }


# Profile Management Views
class AdminProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the admin's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        return self.request.user


class AdminChangePasswordView(APIView):
    """
    API endpoint for changing the admin's password.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')

        if not old_password or not new_password or not new_password2:
            return Response({"error": "All password fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password2:
            return Response({"error": "New passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        # Log the password change
        UserLog.objects.create(
            user=user,
            action='password_change',
            details='Admin changed their password',
            ip_address=request.META.get('REMOTE_ADDR')
        )

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


# Media Management Views
class MediaFileListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating media files.
    """
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = MediaFile.objects.all()

        # Filter by media type
        media_type = self.request.query_params.get('media_type')
        if media_type:
            queryset = queryset.filter(media_type=media_type)

        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)

        return queryset

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class MediaFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, or deleting a media file.
    """
    serializer_class = MediaFileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = MediaFile.objects.all()


# Service Media Management Views
class ServiceMediaCreateView(generics.CreateAPIView):
    serializer_class = ServiceMediaSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
        service_id = self.kwargs.get('service_id')
        service = get_object_or_404(Service, id=service_id)

        # If this is set as primary, unset any existing primary
        if serializer.validated_data.get('is_primary', False):
            ServiceMedia.objects.filter(service=service, is_primary=True).update(is_primary=False)

        serializer.save(service=service)


class ServiceMediaDeleteView(generics.DestroyAPIView):
    serializer_class = ServiceMediaSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = ServiceMedia.objects.all()


# Admin Login View
class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user and user.role == 'admin':
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'detail': 'Invalid credentials or not an admin'}, status=401)
