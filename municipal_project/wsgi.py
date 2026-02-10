"""
WSGI config for municipal_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "municipal_project.settings")

# Failsafe: Run migrations and setup_data if tables are missing (for Render SQLite fallback)
import sys
from django.core.management import call_command

try:
    call_command("migrate")
    call_command("setup_data")
except Exception as e:
    print(f"WSGI Startup Error: {e}", file=sys.stderr)

application = get_wsgi_application()
