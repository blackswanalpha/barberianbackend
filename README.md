# Barberian Backend

A Django-based backend API for the Barberian barbershop appointment system.

## Features

- User authentication with JWT tokens
- Appointment scheduling and management
- Staff and service management
- Client profiles and booking history
- Notification system for appointments

## Tech Stack

- Django 4.2
- Django REST Framework
- PostgreSQL (configurable)
- JWT Authentication

## Installation

1. Clone the repository
   ```
   git clone https://github.com/blackswanalpha/barberianbackend.git
   cd barberianbackend
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run migrations
   ```
   python manage.py migrate
   ```

5. Create a superuser
   ```
   python manage.py createsuperuser
   ```

6. Run the development server
   ```
   python manage.py runserver
   ```

## API Endpoints

- `/api/` - API root
- `/api/appointments/` - Appointment management
- `/api/services/` - Service management
- `/api/barbers/` - Staff management
- `/api/auth/` - Authentication endpoints

## License

MIT
