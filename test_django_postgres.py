import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_django_orm():
    """Test Django ORM with PostgreSQL"""
    print("\nTesting Django ORM with PostgreSQL...")
    
    try:
        from django.db import connection
        from api.models import Barber, Service, Appointment
        from django.contrib.auth.models import User
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"PostgreSQL version via Django: {version[0]}")
        
        # Test ORM operations
        # 1. Count existing users
        user_count = User.objects.count()
        print(f"Existing users: {user_count}")
        
        # 2. Create a test user if none exists
        if user_count == 0:
            test_user = User.objects.create_user(
                username="testuser",
                email="test@example.com",
                password="password123"
            )
            print(f"Created test user: {test_user.username}")
        else:
            test_user = User.objects.first()
            print(f"Using existing user: {test_user.username}")
        
        # 3. Create a test service
        test_service = Service.objects.create(
            name="Test Service",
            description="A test service for PostgreSQL testing",
            price=25.00,
            duration_minutes=30
        )
        print(f"Created test service: {test_service.name}")
        
        # 4. Create a test barber
        test_barber, created = Barber.objects.get_or_create(
            user=test_user,
            defaults={
                "phone_number": "555-123-4567",
                "bio": "Test barber for PostgreSQL testing",
                "years_of_experience": 5
            }
        )
        if created:
            print(f"Created test barber: {test_barber}")
        else:
            print(f"Using existing barber: {test_barber}")
        
        # 5. Query and display data
        services = Service.objects.all()
        print(f"Services in database: {services.count()}")
        for service in services:
            print(f"  - {service.name}: ${service.price}")
        
        print("Django ORM test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_django_orm()
