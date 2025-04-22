import requests
import json
from datetime import datetime, timedelta

# Base URL for the API
BASE_URL = 'http://localhost:8003/api'

# Client credentials
EMAIL = 'kams@gmail.com'
PASSWORD = 'kams1234'

def login():
    """Login with the provided credentials"""
    print(f"\n=== Logging in with {EMAIL} ===")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        'email': EMAIL,
        'password': PASSWORD
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Login successful: {result['user']['first_name']} {result['user']['last_name']}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def get_services(access_token):
    """Get available services"""
    print("\n=== Getting available services ===")
    
    url = f"{BASE_URL}/services/"
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            services = response.json()
            print(f"Found {len(services)} services:")
            for service in services:
                print(f"  - ID: {service['id']}, Name: {service['name']}, Price: ${service['price']}, Duration: {service['duration_minutes']} minutes")
            return services
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

def get_staff(access_token):
    """Get available staff (barbers)"""
    print("\n=== Getting available staff ===")
    
    url = f"{BASE_URL}/staff/"
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            staff = response.json()
            print(f"Found {len(staff)} staff members:")
            for member in staff:
                print(f"  - ID: {member['id']}, Name: {member['user']['first_name']} {member['user']['last_name']}")
            return staff
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

def check_staff_availability(staff_id, date, service_id, access_token):
    """Check staff availability for a specific date"""
    print(f"\n=== Checking availability for staff ID {staff_id} on {date} ===")
    
    url = f"{BASE_URL}/staff/{staff_id}/availability/"
    params = {'date': date}
    if service_id:
        params['service'] = service_id
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            availability = response.json()
            print(f"Available: {availability['available']}")
            print(f"Found {len(availability['slots'])} available time slots")
            if availability['slots']:
                for i, slot in enumerate(availability['slots'][:5]):  # Show first 5 slots
                    print(f"  - Slot {i+1}: {slot['start']} - {slot['end']}")
                if len(availability['slots']) > 5:
                    print(f"  ... and {len(availability['slots']) - 5} more slots")
            return availability
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def book_appointment(access_token, service_id, staff_id, date, time_slot, notes=""):
    """Book an appointment"""
    print(f"\n=== Booking appointment ===")
    print(f"Service ID: {service_id}, Staff ID: {staff_id}")
    print(f"Date: {date}, Time: {time_slot}")
    
    url = f"{BASE_URL}/appointments/create_appointment/"
    data = {
        'service': service_id,
        'staff': staff_id,
        'start_time': f"{date}T{time_slot}:00",
        'notes': notes
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {access_token}"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Appointment booked successfully!")
            print(f"Appointment ID: {result['id']}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def get_client_appointments(access_token):
    """Get client appointments"""
    print("\n=== Getting client appointments ===")
    
    url = f"{BASE_URL}/appointments/"
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            appointments = response.json()
            if isinstance(appointments, list):
                print(f"Found {len(appointments)} appointments:")
                for appointment in appointments:
                    print(f"  - ID: {appointment['id']}")
                    print(f"    Service: {appointment['service']['name']}")
                    print(f"    Date/Time: {appointment['start_time']}")
                    print(f"    Status: {appointment['status']}")
                    print(f"    Staff: {appointment['barber']['user']['first_name']} {appointment['barber']['user']['last_name']}")
                    print()
            else:
                print("Unexpected response format")
            return appointments
        else:
            print(f"Error: {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

def main():
    # Step 1: Login with the provided credentials
    login_data = login()
    
    if not login_data or 'tokens' not in login_data:
        print("Failed to login. Exiting.")
        return
    
    # Get the access token
    access_token = login_data['tokens']['access']
    
    # Step 2: Get available services
    services = get_services(access_token)
    if not services:
        print("No services available. Exiting.")
        return
    
    # Select the first service
    selected_service = services[0]
    
    # Step 3: Get available staff
    staff = get_staff(access_token)
    if not staff:
        print("No staff available. Exiting.")
        return
    
    # Select the first staff member
    selected_staff = staff[0]
    
    # Step 4: Check staff availability for tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    availability = check_staff_availability(selected_staff['id'], tomorrow, selected_service['id'], access_token)
    
    if not availability or not availability['available'] or not availability['slots']:
        print("No available slots for tomorrow. Exiting.")
        return
    
    # Select the first available time slot
    selected_time_slot = availability['slots'][0]['start']
    
    # Step 5: Book the appointment
    booking_result = book_appointment(
        access_token,
        selected_service['id'],
        selected_staff['id'],
        tomorrow,
        selected_time_slot,
        "Appointment booked via script"
    )
    
    if not booking_result:
        print("Failed to book appointment. Exiting.")
        return
    
    # Step 6: View client appointments
    appointments = get_client_appointments(access_token)
    
    print("\n=== Operation Summary ===")
    print(f"Client: {login_data['user']['first_name']} {login_data['user']['last_name']} ({login_data['user']['email']})")
    print(f"Appointment Booked: {'✅ Success' if booking_result else '❌ Failed'}")
    print(f"Appointments Retrieved: {'✅ Success' if appointments else '❌ Failed'}")

if __name__ == "__main__":
    main()
