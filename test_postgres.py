import os
import django
import psycopg2
from psycopg2 import sql

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_postgres_connection():
    """Test direct PostgreSQL connection"""
    print("Testing direct PostgreSQL connection...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname="barberian_db",
            user="barberian_user",
            password="barberian_password",
            host="localhost",
            port="5432"
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Execute a test query
        cur.execute("SELECT version();")
        
        # Fetch the result
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        # Create a test table
        cur.execute(
            sql.SQL("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        )
        conn.commit()
        print("Created test_table successfully")
        
        # Insert data
        cur.execute(
            sql.SQL("""
            INSERT INTO test_table (name) VALUES (%s) RETURNING id
            """),
            ["Test entry"]
        )
        inserted_id = cur.fetchone()[0]
        conn.commit()
        print(f"Inserted test data with ID: {inserted_id}")
        
        # Query data
        cur.execute("SELECT * FROM test_table")
        rows = cur.fetchall()
        print(f"Query results: {rows}")
        
        # Clean up
        cur.execute("DROP TABLE test_table")
        conn.commit()
        print("Dropped test_table successfully")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
        print("PostgreSQL connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

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
        return False

if __name__ == "__main__":
    # Test direct PostgreSQL connection
    postgres_test = test_postgres_connection()
    
    # Test Django ORM with PostgreSQL
    if postgres_test:
        django_test = test_django_orm()
    else:
        print("Skipping Django ORM test due to PostgreSQL connection failure")
