import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')
django.setup()

from barberian.common.models import User

def create_admin_user():
    """Create an admin user"""
    try:
        # Check if admin user already exists
        if User.objects.filter(email='admin@example.com').exists():
            print("Admin user already exists")
            return
        
        # Create admin user
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin1234',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created admin user: {admin.email}")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()
