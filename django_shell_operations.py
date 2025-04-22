import os
import django
import sys
from datetime import datetime, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

def get_or_create_client(email, password, first_name, last_name):
    """Get or create a client user"""
    print(f"\n=== Getting or creating client: {first_name} {last_name} ({email}) ===")
    
    # Check if user already exists
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"User already exists: {user.first_name} {user.last_name}")
        # Update password
        user.set_password(password)
        user.save()
        return user
    
    # Create new user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"Client created successfully: {user.first_name} {user.last_name}")
    return user

def get_services():
    """Get available services"""
    print("\n=== Getting available services ===")
    
    services = Service.objects.all()
    print(f"Found {services.count()} services:")
    for service in services:
        print(f"  - ID: {service.id}, Name: {service.name}, Price: ${service.price}, Duration: {service.duration_minutes} minutes")
    return services

def get_barbers():
    """Get available barbers"""
    print("\n=== Getting available barbers ===")
    
    barbers = Barber.objects.all()
    print(f"Found {barbers.count()} barbers:")
    for barber in barbers:
        print(f"  - ID: {barber.id}, Name: {barber.user.first_name} {barber.user.last_name}")
    return barbers

def book_appointment(client, service, barber, date, start_time, notes=""):
    """Book an appointment"""
    print(f"\n=== Booking appointment ===")
    print(f"Client: {client.first_name} {client.last_name}")
    print(f"Service: {service.name}")
    print(f"Barber: {barber.user.first_name} {barber.user.last_name}")
    print(f"Date: {date}, Time: {start_time}")
    
    # Calculate end time based on service duration
    start_datetime = datetime.combine(date, start_time)
    end_datetime = start_datetime + timedelta(minutes=service.duration_minutes)
    end_time = end_datetime.time()
    
    # Create the appointment
    appointment = Appointment.objects.create(
        client=client,
        barber=barber,
        service=service,
        date=date,
        start_time=start_time,
        end_time=end_time,
        status='scheduled',
        notes=notes
    )
    
    print(f"Appointment booked successfully!")
    print(f"Appointment ID: {appointment.id}")
    print(f"Date/Time: {appointment.date} {appointment.start_time}")
    return appointment

def get_client_appointments(client):
    """Get client appointments"""
    print(f"\n=== Getting appointments for {client.first_name} {client.last_name} ===")
    
    appointments = Appointment.objects.filter(client=client)
    print(f"Found {appointments.count()} appointments:")
    for appointment in appointments:
        print(f"  - ID: {appointment.id}")
        print(f"    Service: {appointment.service.name}")
        print(f"    Date/Time: {appointment.date} {appointment.start_time}")
        print(f"    Status: {appointment.status}")
        print(f"    Barber: {appointment.barber.user.first_name} {appointment.barber.user.last_name}")
        print()
    return appointments

def main():
    # Client details
    email = "kams@gmail.com"
    password = "kams1234"
    first_name = "Kams"
    last_name = "Test"
    
    # Step 1: Get or create client
    client = get_or_create_client(email, password, first_name, last_name)
    
    # Step 2: Get available services
    services = get_services()
    if not services:
        print("No services available. Exiting.")
        return
    
    # Select the first service
    selected_service = services.first()
    
    # Step 3: Get available barbers
    barbers = get_barbers()
    if not barbers:
        print("No barbers available. Exiting.")
        return
    
    # Select the first barber
    selected_barber = barbers.first()
    
    # Step 4: Book the appointment for tomorrow
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    # Generate a random time between 9 AM and 5 PM
    hour = random.randint(9, 17)
    minute = random.choice([0, 30])  # Either on the hour or half hour
    appointment_time = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
    
    # Book the appointment
    appointment = book_appointment(
        client,
        selected_service,
        selected_barber,
        tomorrow,
        appointment_time,
        "Test appointment booked via Django shell"
    )
    
    # Step 5: View client appointments
    appointments = get_client_appointments(client)
    
    print("\n=== Operation Summary ===")
    print(f"Client: {first_name} {last_name} ({email})")
    print(f"Appointment Booked: {'✅ Success' if appointment else '❌ Failed'}")
    print(f"Appointments Retrieved: {'✅ Success' if appointments else '❌ Failed'}")

if __name__ == "__main__":
    main()
