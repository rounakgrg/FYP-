"""
WSGI config for municipal_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys

# Set settings module BEFORE any Django imports
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "municipal_project.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "municipal_project.settings"
print(f"DEBUG: DJANGO_SETTINGS_MODULE set to: {os.environ.get('DJANGO_SETTINGS_MODULE')}", file=sys.stderr)

from django.core.wsgi import get_wsgi_application
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
