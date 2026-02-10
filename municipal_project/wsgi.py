"""
WSGI config for municipal_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Failsafe: Run migrations and setup_data if tables are missing (for Render SQLite fallback)
import sys
import django
from django.core.management import call_command

django.setup()

try:
    # Check if we need to migrate (simple check to avoid concurrency spam if possible, 
    # but migrate is idempotent so calling it is safe-ish)
    print("Running startup migrations...", file=sys.stderr)
    call_command("migrate")
    call_command("setup_data")
    print("Startup migrations completed.", file=sys.stderr)
except Exception as e:
    print(f"WSGI Startup Error: {e}", file=sys.stderr)

application = get_wsgi_application()
