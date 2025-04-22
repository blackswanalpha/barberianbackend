import requests
import json
import sys

# Base URL for API
BASE_URL = 'http://localhost:8001/api'

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    
    # Registration data
    register_data = {
        'email': 'testuser@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    # Return the tokens if successful
    if response.status_code == 201:
        return response.json().get('tokens', {})
    return None

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    
    # Login data
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    # Return the tokens if successful
    if response.status_code == 200:
        return response.json().get('tokens', {})
    return None

def test_services(access_token=None):
    """Test getting services"""
    print("\n=== Testing Services API ===")
    
    # Set up headers if token is provided
    headers = {}
    if access_token:
        headers['Authorization'] = f"Bearer {access_token}"
    
    # Make the request
    response = requests.get(f"{BASE_URL}/services/", headers=headers)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_staff(access_token=None):
    """Test getting staff"""
    print("\n=== Testing Staff API ===")
    
    # Set up headers if token is provided
    headers = {}
    if access_token:
        headers['Authorization'] = f"Bearer {access_token}"
    
    # Make the request
    response = requests.get(f"{BASE_URL}/staff/", headers=headers)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    # Return the first staff member ID if available
    if response.status_code == 200:
        staff_list = response.json()
        if staff_list:
            return staff_list[0]['id']
    return None

def test_staff_availability(staff_id, access_token=None):
    """Test staff availability"""
    print("\n=== Testing Staff Availability API ===")
    
    # Set up headers if token is provided
    headers = {}
    if access_token:
        headers['Authorization'] = f"Bearer {access_token}"
    
    # Make the request
    response = requests.get(f"{BASE_URL}/staff/{staff_id}/availability/?date=2023-12-01", headers=headers)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_booking(staff_id, service_id, access_token=None):
    """Test booking an appointment"""
    print("\n=== Testing Booking API ===")
    
    # Booking data
    booking_data = {
        'service': service_id,
        'staff': staff_id,
        'date': '2023-12-01',
        'time_slot': '10:00',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'phone_number': '555-123-4567',
        'notes': 'Test booking from API'
    }
    
    # Set up headers if token is provided
    headers = {}
    if access_token:
        headers['Authorization'] = f"Bearer {access_token}"
    
    # Make the request
    response = requests.post(f"{BASE_URL}/booking/", json=booking_data, headers=headers)
    
    # Print the response
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    """Main function to run all tests"""
    # Test registration
    tokens = test_register()
    
    # If registration failed, try login
    if not tokens:
        tokens = test_login()
    
    # Get access token
    access_token = tokens.get('access') if tokens else None
    
    # Test services API
    test_services(access_token)
    
    # Test staff API
    staff_id = test_staff(access_token)
    
    # Test staff availability
    if staff_id:
        test_staff_availability(staff_id, access_token)
        
        # Test booking
        service_id = 1  # Assuming service ID 1 exists
        test_booking(staff_id, service_id, access_token)

if __name__ == "__main__":
    main()
