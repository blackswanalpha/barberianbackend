from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment
from django.db.models import Count, Avg, Sum, F, Q
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Test advanced database queries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing advanced queries on MySQL database...'))
        
        # 1. Filtering with Q objects (OR conditions)
        self.stdout.write(self.style.NOTICE('\n--- Filtering with Q objects ---'))
        # Find appointments that are either completed or with John Smith
        john = User.objects.filter(first_name='John', last_name='Smith').first()
        if john:
            john_barber = Barber.objects.get(user=john)
            complex_filter = Appointment.objects.filter(
                Q(status='completed') | Q(barber=john_barber)
            )
            self.stdout.write(f"Appointments that are completed OR with John Smith: {complex_filter.count()}")
            for appt in complex_filter:
                self.stdout.write(f"- {appt.client.get_full_name()} with {appt.barber.user.get_full_name()} on {appt.date} ({appt.status})")
        
        # 2. Aggregation
        self.stdout.write(self.style.NOTICE('\n--- Aggregation queries ---'))
        # Average price of services
        avg_price = Service.objects.aggregate(avg_price=Avg('price'))
        self.stdout.write(f"Average service price: ${avg_price['avg_price']:.2f}")
        
        # Total duration of all services
        total_duration = Service.objects.aggregate(total_minutes=Sum('duration_minutes'))
        self.stdout.write(f"Total duration of all services: {total_duration['total_minutes']} minutes")
        
        # 3. Annotation
        self.stdout.write(self.style.NOTICE('\n--- Annotation queries ---'))
        # Count appointments per barber
        barber_stats = Barber.objects.annotate(appointment_count=Count('barber_appointments'))
        for barber in barber_stats:
            self.stdout.write(f"{barber.user.get_full_name()} has {barber.appointment_count} appointments")
        
        # 4. F expressions
        self.stdout.write(self.style.NOTICE('\n--- F expressions ---'))
        # Find services where the price per minute is greater than $0.50
        expensive_services = Service.objects.filter(price__gt=F('duration_minutes') * 0.5)
        self.stdout.write("Services with price per minute > $0.50:")
        for service in expensive_services:
            price_per_minute = service.price / service.duration_minutes
            self.stdout.write(f"- {service.name}: ${price_per_minute:.2f} per minute (${service.price} for {service.duration_minutes} minutes)")
        
        # 5. Dates and times
        self.stdout.write(self.style.NOTICE('\n--- Date queries ---'))
        # Find appointments in the next 7 days
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        upcoming = Appointment.objects.filter(date__range=[today, next_week])
        self.stdout.write(f"Appointments in the next 7 days: {upcoming.count()}")
        for appt in upcoming:
            self.stdout.write(f"- {appt.client.get_full_name()} with {appt.barber.user.get_full_name()} on {appt.date}")
        
        # 6. Distinct values
        self.stdout.write(self.style.NOTICE('\n--- Distinct queries ---'))
        # Get distinct appointment dates
        distinct_dates = Appointment.objects.values_list('date', flat=True).distinct()
        self.stdout.write(f"Distinct appointment dates: {len(distinct_dates)}")
        for date in distinct_dates:
            self.stdout.write(f"- {date}")
        
        self.stdout.write(self.style.SUCCESS('\nAdvanced queries testing complete!'))
