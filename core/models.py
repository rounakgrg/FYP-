from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CITIZEN', 'Citizen'),
        ('SECTION_USER', 'Section User'),
        ('OFFICE_ADMIN', 'Office Admin'),
        ('SPOKESPERSON', 'Spokesperson'),
        ('SUPER_ADMIN', 'Super Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CITIZEN')
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

    def is_citizen(self): return self.role == 'CITIZEN'
    def is_section_user(self): return self.role == 'SECTION_USER'
    def is_office_admin(self): return self.role == 'OFFICE_ADMIN'
    def is_spokesperson(self): return self.role == 'SPOKESPERSON'
    def is_super_admin(self): return self.role == 'SUPER_ADMIN'

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ServiceCharter(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text="List required documents")
    processing_time = models.CharField(max_length=100, help_text="e.g. 3-5 days")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.title

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    tracking_id = models.CharField(max_length=50, unique=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True, help_text="Location of the issue")
    image = models.ImageField(upload_to='complaints/', null=True, blank=True, help_text="Optional image of the issue")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser_info = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            import uuid
            self.tracking_id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_id} - {self.title}"

class ComplaintRemark(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='remarks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remark = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remark by {self.user} on {self.complaint}"
