#!/usr/bin/env python
"""Script to run the Django server."""
import os
import subprocess

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    # Run server on port 8000 and allow connections from all hosts
    subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:8001"])
