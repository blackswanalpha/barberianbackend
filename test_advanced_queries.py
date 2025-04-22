import os
import django
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Sum, F, Q

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

def test_advanced_queries():
    print("Testing advanced queries on MySQL database...")
    
    # 1. Filtering with Q objects (OR conditions)
    print("\n--- Filtering with Q objects ---")
    # Find appointments that are either completed or with John Smith
    john = User.objects.filter(first_name='John', last_name='Smith').first()
    if john:
        john_barber = Barber.objects.get(user=john)
        complex_filter = Appointment.objects.filter(
            Q(status='completed') | Q(barber=john_barber)
        )
        print(f"Appointments that are completed OR with John Smith: {complex_filter.count()}")
        for appt in complex_filter:
            print(f"- {appt.client.get_full_name()} with {appt.barber.user.get_full_name()} on {appt.date} ({appt.status})")
    
    # 2. Aggregation
    print("\n--- Aggregation queries ---")
    # Average price of services
    avg_price = Service.objects.aggregate(avg_price=Avg('price'))
    print(f"Average service price: ${avg_price['avg_price']:.2f}")
    
    # Total duration of all services
    total_duration = Service.objects.aggregate(total_minutes=Sum('duration_minutes'))
    print(f"Total duration of all services: {total_duration['total_minutes']} minutes")
    
    # 3. Annotation
    print("\n--- Annotation queries ---")
    # Count appointments per barber
    barber_stats = Barber.objects.annotate(appointment_count=Count('barber_appointments'))
    for barber in barber_stats:
        print(f"{barber.user.get_full_name()} has {barber.appointment_count} appointments")
    
    # 4. F expressions
    print("\n--- F expressions ---")
    # Find services where the price per minute is greater than $0.50
    expensive_services = Service.objects.filter(price__gt=F('duration_minutes') * 0.5)
    print("Services with price per minute > $0.50:")
    for service in expensive_services:
        price_per_minute = service.price / service.duration_minutes
        print(f"- {service.name}: ${price_per_minute:.2f} per minute (${service.price} for {service.duration_minutes} minutes)")
    
    # 5. Dates and times
    print("\n--- Date queries ---")
    # Find appointments in the next 7 days
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    upcoming = Appointment.objects.filter(date__range=[today, next_week])
    print(f"Appointments in the next 7 days: {upcoming.count()}")
    for appt in upcoming:
        print(f"- {appt.client.get_full_name()} with {appt.barber.user.get_full_name()} on {appt.date}")
    
    # 6. Distinct values
    print("\n--- Distinct queries ---")
    # Get distinct appointment dates
    distinct_dates = Appointment.objects.values_list('date', flat=True).distinct()
    print(f"Distinct appointment dates: {len(distinct_dates)}")
    for date in distinct_dates:
        print(f"- {date}")
    
    print("\nAdvanced queries testing complete!")

if __name__ == '__main__':
    test_advanced_queries()
