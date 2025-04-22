import os
import django
import json
import requests
from datetime import datetime, timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from api.models import Barber, Service, Appointment

# Base URL for API
BASE_URL = 'http://localhost:8000/api'

def get_auth_token():
    """Get authentication token for admin user"""
    # For Django REST Framework's built-in authentication
    session = requests.Session()

    # First, get the CSRF token by visiting the API root
    response = session.get(f"{BASE_URL}/")
    csrf_token = session.cookies.get('csrftoken')

    # Now try to authenticate using Django REST Framework's session auth
    auth_url = f"{BASE_URL}/auth/login/"
    login_data = {
        'username': 'admin',
        'password': 'admin123',
    }
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': BASE_URL,
    }

    response = session.post(auth_url, data=login_data, headers=headers)

    if response.status_code == 200 or response.status_code == 302:
        print("Authentication successful")
        return session
    else:
        print(f"Authentication failed: {response.status_code}")
        print(response.text)
        return None

def test_admin_crud():
    """Test CRUD operations as admin"""
    print("\n=== Testing Admin CRUD Operations ===")

    # Get authentication
    session = get_auth_token()
    if not session:
        return

    # 1. CREATE: Create a new service
    print("\n--- Creating a new service ---")
    new_service_data = {
        'name': 'Premium Shave',
        'description': 'Luxury hot towel shave with premium products',
        'price': '35.00',
        'duration_minutes': 45
    }

    response = session.post(f"{BASE_URL}/services/", data=new_service_data)
    if response.status_code == 201:
        service_id = response.json()['id']
        print(f"Service created successfully with ID: {service_id}")
    else:
        print(f"Failed to create service: {response.status_code}")
        print(response.text)
        return

    # 2. READ: Get the service details
    print("\n--- Reading service details ---")
    response = session.get(f"{BASE_URL}/services/{service_id}/")
    if response.status_code == 200:
        service_data = response.json()
        print(f"Service details: {json.dumps(service_data, indent=2)}")
    else:
        print(f"Failed to get service: {response.status_code}")

    # 3. UPDATE: Update the service
    print("\n--- Updating service ---")
    update_data = {
        'name': 'Deluxe Premium Shave',
        'price': '40.00'
    }

    response = session.patch(f"{BASE_URL}/services/{service_id}/", data=update_data)
    if response.status_code == 200:
        updated_data = response.json()
        print(f"Service updated successfully: {json.dumps(updated_data, indent=2)}")
    else:
        print(f"Failed to update service: {response.status_code}")
        print(response.text)

    # 4. DELETE: Delete the service
    print("\n--- Deleting service ---")
    response = session.delete(f"{BASE_URL}/services/{service_id}/")
    if response.status_code == 204:
        print("Service deleted successfully")
    else:
        print(f"Failed to delete service: {response.status_code}")
        print(response.text)

    # 5. Verify deletion
    print("\n--- Verifying deletion ---")
    response = session.get(f"{BASE_URL}/services/{service_id}/")
    if response.status_code == 404:
        print("Service deletion verified (404 Not Found)")
    else:
        print(f"Service still exists: {response.status_code}")

def test_client_crud():
    """Test CRUD operations as a client"""
    print("\n=== Testing Client CRUD Operations ===")

    # Create a client session
    session = requests.Session()

    # First, get the CSRF token by visiting the API root
    response = session.get(f"{BASE_URL}/")
    csrf_token = session.cookies.get('csrftoken')

    # Now try to authenticate using Django REST Framework's session auth
    auth_url = f"{BASE_URL}/auth/login/"
    login_data = {
        'username': 'client1',
        'password': 'password123',
    }
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': BASE_URL,
    }

    response = session.post(auth_url, data=login_data, headers=headers)

    if response.status_code != 200:
        print(f"Client authentication failed: {response.status_code}")
        return

    print("Client authentication successful")

    # 1. READ: Get available services
    print("\n--- Reading available services ---")
    response = session.get(f"{BASE_URL}/services/")
    if response.status_code == 200:
        services = response.json()
        print(f"Available services: {len(services)} services found")
        service_id = services[0]['id']  # Use the first service for appointment
    else:
        print(f"Failed to get services: {response.status_code}")
        return

    # 2. READ: Get available barbers
    print("\n--- Reading available barbers ---")
    response = session.get(f"{BASE_URL}/barbers/")
    if response.status_code == 200:
        barbers = response.json()
        print(f"Available barbers: {len(barbers)} barbers found")
        barber_id = barbers[0]['id']  # Use the first barber for appointment
    else:
        print(f"Failed to get barbers: {response.status_code}")
        return

    # 3. CREATE: Book an appointment
    print("\n--- Creating a new appointment ---")
    # Schedule for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    appointment_data = {
        'barber': barber_id,
        'service': service_id,
        'date': tomorrow,
        'start_time': '14:00:00',
        'end_time': '14:30:00',
        'notes': 'Test appointment from API'
    }

    response = session.post(f"{BASE_URL}/appointments/", data=appointment_data)
    if response.status_code == 201:
        appointment = response.json()
        appointment_id = appointment['id']
        print(f"Appointment created successfully with ID: {appointment_id}")
    else:
        print(f"Failed to create appointment: {response.status_code}")
        print(response.text)
        return

    # 4. READ: Get appointment details
    print("\n--- Reading appointment details ---")
    response = session.get(f"{BASE_URL}/appointments/{appointment_id}/")
    if response.status_code == 200:
        appointment_data = response.json()
        print(f"Appointment details: {json.dumps(appointment_data, indent=2)}")
    else:
        print(f"Failed to get appointment: {response.status_code}")

    # 5. UPDATE: Update appointment notes
    print("\n--- Updating appointment ---")
    update_data = {
        'notes': 'Updated test appointment notes'
    }

    response = session.patch(f"{BASE_URL}/appointments/{appointment_id}/", data=update_data)
    if response.status_code == 200:
        updated_data = response.json()
        print(f"Appointment updated successfully")
    else:
        print(f"Failed to update appointment: {response.status_code}")
        print(response.text)

    # 6. DELETE: Cancel appointment (in a real app, this might be a status change rather than deletion)
    print("\n--- Cancelling appointment ---")
    response = session.delete(f"{BASE_URL}/appointments/{appointment_id}/")
    if response.status_code == 204:
        print("Appointment cancelled successfully")
    else:
        print(f"Failed to cancel appointment: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test admin CRUD operations
    test_admin_crud()

    # Test client CRUD operations
    test_client_crud()
