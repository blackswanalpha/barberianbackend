import os
import django
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

def test_crud_operations():
    print("Testing CRUD operations on MySQL database...")
    
    # CREATE
    print("\n--- CREATE Operations ---")
    
    # Create a new service
    new_service = Service.objects.create(
        name="Premium Haircut",
        description="Luxury haircut with styling and hair products.",
        price=50.00,
        duration_minutes=45
    )
    print(f"Created new service: {new_service.name}, ID: {new_service.id}")
    
    # READ
    print("\n--- READ Operations ---")
    
    # Read all services
    services = Service.objects.all()
    print(f"Total services: {services.count()}")
    for service in services:
        print(f"Service: {service.name}, Price: ${service.price}, Duration: {service.duration_minutes} minutes")
    
    # Read all barbers
    barbers = Barber.objects.all()
    print(f"\nTotal barbers: {barbers.count()}")
    for barber in barbers:
        print(f"Barber: {barber.user.get_full_name()}, Experience: {barber.years_of_experience} years")
    
    # Read all appointments
    appointments = Appointment.objects.all()
    print(f"\nTotal appointments: {appointments.count()}")
    for appointment in appointments:
        print(f"Appointment: {appointment.client.get_full_name()} with {appointment.barber.user.get_full_name()} on {appointment.date} at {appointment.start_time}")
    
    # UPDATE
    print("\n--- UPDATE Operations ---")
    
    # Update the price of the new service
    new_service.price = 55.00
    new_service.save()
    print(f"Updated service price: {new_service.name} now costs ${new_service.price}")
    
    # Find the first appointment and update its status
    if appointments.exists():
        first_appointment = appointments.first()
        old_status = first_appointment.status
        first_appointment.status = 'completed'
        first_appointment.save()
        print(f"Updated appointment status from '{old_status}' to '{first_appointment.status}'")
    
    # DELETE
    print("\n--- DELETE Operations ---")
    
    # Delete the service we created
    service_name = new_service.name
    new_service.delete()
    print(f"Deleted service: {service_name}")
    
    # Verify deletion
    try:
        Service.objects.get(name="Premium Haircut")
        print("Service still exists!")
    except Service.DoesNotExist:
        print("Service successfully deleted!")
    
    print("\nCRUD operations testing complete!")

if __name__ == '__main__':
    test_crud_operations()
