"""
Django WSGI application for Barberian Barber Shop Management System
"""
import os

from django.core.wsgi import get_wsgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barberian.settings')

# This is the variable that gunicorn looks for (must be named "app")
app = get_wsgi_application()

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    import sys
    if len(sys.argv) == 1:
        # If no arguments are provided, run the server
        sys.argv = ["manage.py", "runserver", "0.0.0.0:5000"]
    execute_from_command_line(sys.argv)