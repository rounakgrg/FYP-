from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ServiceCharter, Complaint, ComplaintRemark, Department, User
from .forms import CitizenRegistrationForm, AdminUserCreationForm, ServiceCharterForm
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def home(request):
    return render(request, 'core/home.html')

def service_charter(request):
    services = ServiceCharter.objects.all()
    departments = Department.objects.all()
    return render(request, 'core/service_charter.html', {'services': services, 'departments': departments})

def file_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        dept_id = request.POST.get('department')
        location = request.POST.get('location')
        image = request.FILES.get('image')
        
        # for demo, if user not logged in, we might need a dummy user or require login
        # Plan says "Citizen" role. If user is anon, maybe redirect to login or create anon user?
        # For this requirement "Citizen (Normal User)", let's assume they must be logged in 
        # OR we create a "Guest" account. 
        # But commonly, citizens register. Let's enforce login for now as per "User Management" requirement implies users exist.
        if not request.user.is_authenticated:
             messages.error(request, "Please login to file a complaint.")
             return redirect('login')

        department = get_object_or_404(Department, pk=dept_id) if dept_id else None
        
        complaint = Complaint.objects.create(
            title=title,
            description=description,
            citizen=request.user,
            department=department,
            location=location,
            image=image,
            ip_address=request.META.get('REMOTE_ADDR'),
            browser_info=request.META.get('HTTP_USER_AGENT')
        )
        messages.success(request, f"Complaint submitted! Tracking ID: {complaint.tracking_id}")
        return redirect('track_complaint')
        
    departments = Department.objects.all()
    return render(request, 'core/file_complaint.html', {'departments': departments})

def track_complaint(request):
    complaint = None
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        try:
            complaint = Complaint.objects.get(tracking_id=tracking_id)
        except Complaint.DoesNotExist:
            messages.error(request, "Invalid Tracking ID")
    
    return render(request, 'core/track_complaint.html', {'complaint': complaint})

@login_required
def dashboard(request):
    user = request.user
    if user.is_citizen():
        complaints = Complaint.objects.filter(citizen=user)
        pending_count = 0
        resolved_count = 0
        template = 'core/dashboard_citizen.html'
    elif user.is_office_admin():
        complaints = Complaint.objects.all().order_by('-created_at')
        pending_count = complaints.filter(status='PENDING').count()
        resolved_count = complaints.filter(status='RESOLVED').count()
        template = 'core/dashboard_office_admin.html'
    elif user.is_section_user():
        complaints = Complaint.objects.filter(assigned_to=user)
        pending_count = complaints.filter(status='PENDING').count()
        resolved_count = complaints.filter(status='RESOLVED').count()
        template = 'core/dashboard_section_user.html'
    elif user.is_spokesperson():
        complaints = Complaint.objects.filter(status='RESOLVED') # Example filter
        pending_count = 0
        resolved_count = complaints.count()
        template = 'core/dashboard_spokesperson.html'
    elif user.is_super_admin():
         return redirect('dashboard_super_admin')
    else:
        complaints = []
        pending_count = 0
        resolved_count = 0
        template = 'core/dashboard_citizen.html' # Fallback
        
    return render(request, template, {
        'complaints': complaints,
        'pending_count': pending_count,
        'resolved_count': resolved_count
    })

@login_required
def dashboard_super_admin(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    context = {
        'total_users': User.objects.count(),
        'total_services': ServiceCharter.objects.count(),
        'total_complaints': Complaint.objects.count(),
        'users': User.objects.all()[:5], # Show recent 5 for dashboard overview if needed, but template only uses stats
    }
    return render(request, 'core/dashboard_super_admin.html', context)

@login_required
def admin_users(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'core/admin_users.html', {'users': users})

@login_required
def admin_services(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    services = ServiceCharter.objects.all()
    return render(request, 'core/admin_services.html', {'services': services})

@login_required
def admin_complaints(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    # Reuse office admin dashboard logic but with super admin theme wrapper if desired, 
    # or create a consistent table view. For now, let's just list all.
    complaints = Complaint.objects.all().order_by('-created_at')
    # We can reuse office admin template but we need the theme wrapper. 
    # Better to make a new simple template or reuse logic.
    # For now, let's duplicate the layout for consistency with tabs.
    return render(request, 'core/dashboard_office_admin.html', {'complaints': complaints, 'is_super_admin': True})

@login_required
def admin_user_complaints(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=pk)
    complaints = Complaint.objects.filter(citizen=target_user).order_by('-created_at')
    
    return render(request, 'core/admin_user_complaints.html', {
        'target_user': target_user,
        'complaints': complaints
    })

@login_required
def admin_complaint_detail(request, pk):
    # Allow office admins, section users, super admins to view
    if request.user.is_citizen():
        return redirect('dashboard')
    complaint = get_object_or_404(Complaint, pk=pk)
    
    from .forms import ComplaintAssignmentForm, ComplaintStatusUpdateForm
    
    assign_form = None
    status_form = None
    
    can_assign = request.user.is_office_admin() or request.user.is_super_admin()
    can_update = request.user.is_section_user() or request.user.is_office_admin() or request.user.is_super_admin()
    
    if request.method == 'POST':
        if 'assign' in request.POST and can_assign:
            assign_form = ComplaintAssignmentForm(request.POST, instance=complaint)
            if assign_form.is_valid():
                assign_form.save()
                messages.success(request, 'Complaint assignment updated.')
                return redirect('admin_complaint_detail', pk=pk)
        elif 'update_status' in request.POST and can_update:
            status_form = ComplaintStatusUpdateForm(request.POST, instance=complaint)
            if status_form.is_valid():
                complaint = status_form.save()
                remark_text = status_form.cleaned_data.get('remark')
                if remark_text:
                    ComplaintRemark.objects.create(
                        complaint=complaint,
                        user=request.user,
                        remark=remark_text
                    )
                messages.success(request, 'Complaint status updated.')
                return redirect('admin_complaint_detail', pk=pk)

    if can_assign:
        assign_form = ComplaintAssignmentForm(instance=complaint) if assign_form is None else assign_form
    if can_update:
        status_form = ComplaintStatusUpdateForm(instance=complaint) if status_form is None else status_form
        
    return render(request, 'core/admin_complaint_detail.html', {
        'complaint': complaint, 
        'is_super_admin': request.user.is_super_admin(),
        'assign_form': assign_form,
        'status_form': status_form,
        'can_assign': can_assign,
        'can_update': can_update
    })

@login_required
def admin_user_add(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('admin_users')
        else:
            print(f"Form Errors: {form.errors}")
    else:
        form = AdminUserCreationForm()
    return render(request, 'core/admin_user_form.html', {'form': form, 'title': 'Add New User'})

@login_required
def admin_service_add(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ServiceCharterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully.')
            return redirect('admin_services')
    else:
        form = ServiceCharterForm()
    return render(request, 'core/admin_service_form.html', {'form': form, 'title': 'Add New Service'})

@login_required
def admin_service_edit(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    
    service = get_object_or_404(ServiceCharter, pk=pk)
    if request.method == 'POST':
        form = ServiceCharterForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('admin_services')
    else:
        form = ServiceCharterForm(instance=service)
    return render(request, 'core/admin_service_form.html', {'form': form, 'title': 'Edit Service'})

@login_required
def admin_service_delete(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    service = get_object_or_404(ServiceCharter, pk=pk)
    if request.method == 'POST':
        service.delete()
@login_required
def dashboard(request):
    user = request.user
    if user.is_citizen():
        complaints = Complaint.objects.filter(citizen=user)
        pending_count = 0
        resolved_count = 0
        template = 'core/dashboard_citizen.html'
    elif user.is_office_admin():
        complaints = Complaint.objects.all().order_by('-created_at')
        pending_count = complaints.filter(status='PENDING').count()
        resolved_count = complaints.filter(status='RESOLVED').count()
        template = 'core/dashboard_office_admin.html'
    elif user.is_section_user():
        complaints = Complaint.objects.filter(assigned_to=user)
        pending_count = complaints.filter(status='PENDING').count()
        resolved_count = complaints.filter(status='RESOLVED').count()
        template = 'core/dashboard_section_user.html'
    elif user.is_spokesperson():
        complaints = Complaint.objects.filter(status='RESOLVED') # Example filter
        pending_count = 0
        resolved_count = complaints.count()
        template = 'core/dashboard_spokesperson.html'
    elif user.is_super_admin():
         return redirect('dashboard_super_admin')
    else:
        complaints = []
        pending_count = 0
        resolved_count = 0
        template = 'core/dashboard_citizen.html' # Fallback
        
    return render(request, template, {
        'complaints': complaints,
        'pending_count': pending_count,
        'resolved_count': resolved_count
    })

@login_required
def dashboard_super_admin(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    context = {
        'total_users': User.objects.count(),
        'total_services': ServiceCharter.objects.count(),
        'total_complaints': Complaint.objects.count(),
        'users': User.objects.all()[:5], # Show recent 5 for dashboard overview if needed, but template only uses stats
    }
    return render(request, 'core/dashboard_super_admin.html', context)

@login_required
def admin_users(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    users = User.objects.all()
    return render(request, 'core/admin_users.html', {'users': users})

@login_required
def admin_services(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    services = ServiceCharter.objects.all()
    return render(request, 'core/admin_services.html', {'services': services})

@login_required
def admin_complaints(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    # Reuse office admin dashboard logic but with super admin theme wrapper if desired, 
    # or create a consistent table view. For now, let's just list all.
    complaints = Complaint.objects.all().order_by('-created_at')
    # We can reuse office admin template but we need the theme wrapper. 
    # Better to make a new simple template or reuse logic.
    # For now, let's duplicate the layout for consistency with tabs.
    return render(request, 'core/dashboard_office_admin.html', {'complaints': complaints, 'is_super_admin': True})

@login_required
def admin_user_complaints(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    target_user = get_object_or_404(User, pk=pk)
    complaints = Complaint.objects.filter(citizen=target_user).order_by('-created_at')
    
    return render(request, 'core/admin_user_complaints.html', {
        'target_user': target_user,
        'complaints': complaints
    })

@login_required
def admin_complaint_detail(request, pk):
    # Allow office admins, section users, super admins to view
    if request.user.is_citizen():
        return redirect('dashboard')
    complaint = get_object_or_404(Complaint, pk=pk)
    
    from .forms import ComplaintAssignmentForm, ComplaintStatusUpdateForm
    
    assign_form = None
    status_form = None
    
    can_assign = request.user.is_office_admin() or request.user.is_super_admin()
    can_update = request.user.is_section_user() or request.user.is_office_admin() or request.user.is_super_admin()
    
    if request.method == 'POST':
        if 'assign' in request.POST and can_assign:
            assign_form = ComplaintAssignmentForm(request.POST, instance=complaint)
            if assign_form.is_valid():
                assign_form.save()
                messages.success(request, 'Complaint assignment updated.')
                return redirect('admin_complaint_detail', pk=pk)
        elif 'update_status' in request.POST and can_update:
            status_form = ComplaintStatusUpdateForm(request.POST, instance=complaint)
            if status_form.is_valid():
                complaint = status_form.save()
                remark_text = status_form.cleaned_data.get('remark')
                if remark_text:
                    ComplaintRemark.objects.create(
                        complaint=complaint,
                        user=request.user,
                        remark=remark_text
                    )
                messages.success(request, 'Complaint status updated.')
                return redirect('admin_complaint_detail', pk=pk)

    if can_assign:
        assign_form = ComplaintAssignmentForm(instance=complaint) if assign_form is None else assign_form
    if can_update:
        status_form = ComplaintStatusUpdateForm(instance=complaint) if status_form is None else status_form
        
    return render(request, 'core/admin_complaint_detail.html', {
        'complaint': complaint, 
        'is_super_admin': request.user.is_super_admin(),
        'assign_form': assign_form,
        'status_form': status_form,
        'can_assign': can_assign,
        'can_update': can_update
    })

@login_required
def admin_user_add(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('admin_users')
        else:
            print(f"Form Errors: {form.errors}")
    else:
        form = AdminUserCreationForm()
    return render(request, 'core/admin_user_form.html', {'form': form, 'title': 'Add New User'})

@login_required
def admin_service_add(request):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ServiceCharterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added successfully.')
            return redirect('admin_services')
    else:
        form = ServiceCharterForm()
    return render(request, 'core/admin_service_form.html', {'form': form, 'title': 'Add New Service'})

@login_required
def admin_service_edit(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
    
    service = get_object_or_404(ServiceCharter, pk=pk)
    if request.method == 'POST':
        form = ServiceCharterForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('admin_services')
    else:
        form = ServiceCharterForm(instance=service)
    return render(request, 'core/admin_service_form.html', {'form': form, 'title': 'Edit Service'})

@login_required
def admin_service_delete(request, pk):
    if not request.user.is_super_admin():
        return redirect('dashboard')
        
    service = get_object_or_404(ServiceCharter, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
        return redirect('admin_services')
    
    return render(request, 'core/confirm_delete.html', {'object': service, 'title': 'Delete Service'})

@login_required
def export_complaints(request):
    user = request.user
    
    if user.is_super_admin() or user.is_office_admin():
        complaints = Complaint.objects.all().order_by('-created_at').prefetch_related('remarks')
    elif user.is_section_user():
        complaints = Complaint.objects.filter(assigned_to=user).order_by('-created_at').prefetch_related('remarks')
    elif user.is_citizen():
        complaints = Complaint.objects.filter(citizen=user).order_by('-created_at').prefetch_related('remarks')
    elif user.is_spokesperson():
        complaints = Complaint.objects.filter(status='RESOLVED').order_by('-created_at').prefetch_related('remarks')
    else:
        complaints = []

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="detailed_complaints_report.csv"'

    writer = csv.writer(response)
    # Write a detailed header
    writer.writerow([
        'Tracking ID', 
        'Title', 
        'Description', 
        'Citizen (Username)', 
        'Department', 
        'Assigned Official', 
        'Location', 
        'Status', 
        'Latest Remark',
        'Date Created', 
        'Last Updated'
    ])

    for complaint in complaints:
        # Get the latest remark if any
        latest_remark = complaint.remarks.last()
        remark_text = latest_remark.remark if latest_remark else 'No remarks'

        writer.writerow([
            complaint.tracking_id,
            complaint.title,
            complaint.description.replace('\n', ' | ').replace('\r', ''),  # Flatten description for better CSV reading
            complaint.citizen.username if complaint.citizen else 'N/A',
            complaint.department.name if complaint.department else 'Unassigned',
            complaint.assigned_to.username if complaint.assigned_to else 'Unassigned',
            complaint.location if complaint.location else 'Not provided',
            complaint.get_status_display(),
            remark_text.replace('\n', ' | ').replace('\r', ''),
            complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            complaint.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response
