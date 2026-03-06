from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ServiceCharter, Complaint

class CitizenRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fix for standard password fields from UserCreationForm
        # UserCreationForm (from Django) adds password fields dynamically, so we must style them dynamically
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'CITIZEN'
        if commit:
            user.save()
        return user

class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'department']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
             if 'class' not in self.fields[field_name].widget.attrs:
                self.fields[field_name].widget.attrs['class'] = 'form-control'

class ServiceCharterForm(forms.ModelForm):
    class Meta:
        model = ServiceCharter
        fields = ['title', 'description', 'requirements', 'processing_time', 'fee']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'processing_time': forms.TextInput(attrs={'class': 'form-control'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ComplaintAssignmentForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['department', 'assigned_to']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role__in=['SECTION_USER', 'OFFICE_ADMIN'])

class ComplaintStatusUpdateForm(forms.ModelForm):
    remark = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add an optional remark/update...'}), required=False)
    
    class Meta:
        model = Complaint
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
