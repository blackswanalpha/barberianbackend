import os
import django
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

def test_admin_crud():
    """Test CRUD operations as admin"""
    print("\n=== Testing Admin CRUD Operations ===")
    
    # 1. CREATE: Create a new service
    print("\n--- Creating a new service ---")
    new_service = Service.objects.create(
        name="Premium Shave",
        description="Luxury hot towel shave with premium products",
        price=35.00,
        duration_minutes=45
    )
    print(f"Service created successfully with ID: {new_service.id}")
    
    # 2. READ: Get the service details
    print("\n--- Reading service details ---")
    service = Service.objects.get(id=new_service.id)
    print(f"Service details: {service.name}, ${service.price}, {service.duration_minutes} minutes")
    
    # 3. UPDATE: Update the service
    print("\n--- Updating service ---")
    service.name = "Deluxe Premium Shave"
    service.price = 40.00
    service.save()
    
    # Verify update
    updated_service = Service.objects.get(id=new_service.id)
    print(f"Service updated successfully: {updated_service.name}, ${updated_service.price}")
    
    # 4. DELETE: Delete the service
    print("\n--- Deleting service ---")
    service_id = service.id
    service.delete()
    print("Service deleted successfully")
    
    # 5. Verify deletion
    print("\n--- Verifying deletion ---")
    try:
        Service.objects.get(id=service_id)
        print("Service still exists!")
    except Service.DoesNotExist:
        print("Service deletion verified (not found)")

def test_client_crud():
    """Test CRUD operations as a client"""
    print("\n=== Testing Client CRUD Operations ===")
    
    # Get a client user
    try:
        client = User.objects.get(username='client1')
        print(f"Using client: {client.username}")
    except User.DoesNotExist:
        print("Client user not found!")
        return
    
    # 1. READ: Get available services
    print("\n--- Reading available services ---")
    services = Service.objects.all()
    print(f"Available services: {services.count()} services found")
    for service in services:
        print(f"- {service.name}: ${service.price}")
    
    if services.exists():
        service = services.first()
    else:
        print("No services available!")
        return
    
    # 2. READ: Get available barbers
    print("\n--- Reading available barbers ---")
    barbers = Barber.objects.all()
    print(f"Available barbers: {barbers.count()} barbers found")
    for barber in barbers:
        print(f"- {barber.user.get_full_name()}")
    
    if barbers.exists():
        barber = barbers.first()
    else:
        print("No barbers available!")
        return
    
    # 3. CREATE: Book an appointment
    print("\n--- Creating a new appointment ---")
    # Schedule for tomorrow
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    appointment = Appointment.objects.create(
        client=client,
        barber=barber,
        service=service,
        date=tomorrow,
        start_time=datetime.strptime('14:00', '%H:%M').time(),
        end_time=datetime.strptime('14:30', '%H:%M').time(),
        notes='Test appointment from client',
        status='scheduled'
    )
    print(f"Appointment created successfully with ID: {appointment.id}")
    
    # 4. READ: Get appointment details
    print("\n--- Reading appointment details ---")
    appointment = Appointment.objects.get(id=appointment.id)
    print(f"Appointment details: {appointment.client.username} with {appointment.barber.user.get_full_name()} on {appointment.date} at {appointment.start_time}")
    
    # 5. UPDATE: Update appointment notes
    print("\n--- Updating appointment ---")
    appointment.notes = 'Updated test appointment notes'
    appointment.save()
    
    # Verify update
    updated_appointment = Appointment.objects.get(id=appointment.id)
    print(f"Appointment updated successfully: {updated_appointment.notes}")
    
    # 6. DELETE: Cancel appointment (in a real app, this might be a status change rather than deletion)
    print("\n--- Cancelling appointment ---")
    appointment_id = appointment.id
    appointment.delete()
    print("Appointment cancelled successfully")
    
    # Verify deletion
    try:
        Appointment.objects.get(id=appointment_id)
        print("Appointment still exists!")
    except Appointment.DoesNotExist:
        print("Appointment deletion verified (not found)")

if __name__ == "__main__":
    # Test admin CRUD operations
    test_admin_crud()
    
    # Test client CRUD operations
    test_client_crud()
