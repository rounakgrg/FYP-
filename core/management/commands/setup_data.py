from django.core.management.base import BaseCommand
from core.models import User, Department, ServiceCharter

class Command(BaseCommand):
    help = 'Populates initial data for testing'

    def handle(self, *args, **kwargs):
        # Departments
        dept_pw, _ = Department.objects.get_or_create(name='Public Works', description='Infrastructure and Roads')
        dept_health, _ = Department.objects.get_or_create(name='Health', description='Public Health and Licensing')
        dept_water, _ = Department.objects.get_or_create(name='Water & Sanitation', description='Water supply and waste')

        # Services
        ServiceCharter.objects.get_or_create(
            title='Building Permit',
            defaults={
                'description': 'Approval for new construction or renovation.',
                'requirements': 'Site plan, Title deed, ID copy',
                'processing_time': '14 days',
                'fee': 500.00
            }
        )
        ServiceCharter.objects.get_or_create(
            title='Business License',
            defaults={
                'description': 'Permit to operate a business within city limits.',
                'requirements': 'Business registration, Tax PIN, Lease agreement',
                'processing_time': '7 days',
                'fee': 150.00
            }
        )
        
        # Users
        def create_user(username, role, email='test@example.com', dept=None):
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username=username, email=email, password='password', role=role, department=dept)
                self.stdout.write(f'Created user: {username} ({role})')
            else:
                self.stdout.write(f'User {username} already exists')

        create_user('citizen', 'CITIZEN')
        create_user('section_user', 'SECTION_USER', dept=dept_pw)
        create_user('office_admin', 'OFFICE_ADMIN')
        create_user('spokesperson', 'SPOKESPERSON')

        # Super Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='SUPER_ADMIN')
            self.stdout.write('Created Super Admin: admin')

        self.stdout.write(self.style.SUCCESS('Successfully populated data'))
