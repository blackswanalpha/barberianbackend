"""
Direct database settings for Barberian project.
This file contains hardcoded database settings and is imported by settings.py.
"""

# Direct database settings (no environment variables)
DIRECT_DATABASE_SETTINGS = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'barberian',
        'USER': 'barberian_owner',
        'PASSWORD': 'npg_DydTYhfb3zt0',
        'HOST': 'ep-lively-shadow-a2z3iihs-pooler.eu-central-1.aws.neon.tech',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}
