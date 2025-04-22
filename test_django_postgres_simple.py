import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_django_postgres():
    """Test Django ORM with PostgreSQL"""
    print("\nTesting Django ORM with PostgreSQL...")
    
    try:
        from django.db import connection
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"PostgreSQL version via Django: {version[0]}")
        
        # Create a test table
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created django_test_table successfully")
        
        # Insert data
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO django_test_table (name) VALUES (%s) RETURNING id",
                ["Django Test Entry"]
            )
            inserted_id = cursor.fetchone()[0]
            print(f"Inserted test data with ID: {inserted_id}")
        
        # Query data
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM django_test_table")
            rows = cursor.fetchall()
            print(f"Query results: {rows}")
        
        # Clean up
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE django_test_table")
            print("Dropped django_test_table successfully")
        
        print("Django PostgreSQL connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_django_postgres()
