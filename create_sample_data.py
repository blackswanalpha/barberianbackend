import os
import django
import random
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

def create_sample_data():
    print("Creating sample data...")
    
    # Create barbers
    barber_data = [
        {
            'username': 'barber1',
            'email': 'barber1@example.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'password': 'password123',
            'phone_number': '555-123-4567',
            'bio': 'Experienced barber with 5 years of experience in classic cuts.',
            'years_of_experience': 5
        },
        {
            'username': 'barber2',
            'email': 'barber2@example.com',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'password': 'password123',
            'phone_number': '555-987-6543',
            'bio': 'Specializing in modern styles and beard grooming.',
            'years_of_experience': 3
        }
    ]
    
    for data in barber_data:
        # Extract barber-specific fields
        phone_number = data.pop('phone_number')
        bio = data.pop('bio')
        years_of_experience = data.pop('years_of_experience')
        
        # Create user
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"Created user: {user.username}")
        
        # Create barber profile
        barber, created = Barber.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': phone_number,
                'bio': bio,
                'years_of_experience': years_of_experience
            }
        )
        
        if created:
            print(f"Created barber: {barber}")
    
    # Create services
    service_data = [
        {
            'name': 'Haircut',
            'description': 'Basic haircut with clippers and scissors.',
            'price': 25.00,
            'duration_minutes': 30
        },
        {
            'name': 'Beard Trim',
            'description': 'Trim and shape your beard for a clean look.',
            'price': 15.00,
            'duration_minutes': 20
        },
        {
            'name': 'Full Service',
            'description': 'Haircut, beard trim, and hot towel treatment.',
            'price': 40.00,
            'duration_minutes': 60
        }
    ]
    
    for data in service_data:
        service, created = Service.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        
        if created:
            print(f"Created service: {service.name}")
    
    # Create clients
    client_data = [
        {
            'username': 'client1',
            'email': 'client1@example.com',
            'first_name': 'Alex',
            'last_name': 'Johnson',
            'password': 'password123'
        },
        {
            'username': 'client2',
            'email': 'client2@example.com',
            'first_name': 'Sarah',
            'last_name': 'Williams',
            'password': 'password123'
        }
    ]
    
    for data in client_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"Created client: {user.username}")
    
    # Create appointments
    barbers = Barber.objects.all()
    services = Service.objects.all()
    clients = User.objects.filter(username__startswith='client')
    
    if barbers and services and clients:
        # Create a few appointments
        for i in range(5):
            client = random.choice(clients)
            barber = random.choice(barbers)
            service = random.choice(services)
            
            # Random date in the next 14 days
            days_ahead = random.randint(1, 14)
            date = datetime.now().date() + timedelta(days=days_ahead)
            
            # Random time between 9 AM and 5 PM
            hour = random.randint(9, 16)
            start_time = datetime.strptime(f"{hour}:00", "%H:%M").time()
            
            # Calculate end time based on service duration
            end_hour = hour + service.duration_minutes // 60
            end_minute = service.duration_minutes % 60
            end_time = datetime.strptime(f"{end_hour}:{end_minute}", "%H:%M").time()
            
            appointment, created = Appointment.objects.get_or_create(
                client=client,
                barber=barber,
                service=service,
                date=date,
                defaults={
                    'start_time': start_time,
                    'end_time': end_time,
                    'status': 'scheduled'
                }
            )
            
            if created:
                print(f"Created appointment: {client.username} with {barber.user.username} on {date}")
    
    print("Sample data creation complete!")

if __name__ == '__main__':
    create_sample_data()
