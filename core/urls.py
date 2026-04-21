from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.service_charter, name='service_charter'),
    path('complaint/file/', views.file_complaint, name='file_complaint'),
    path('complaint/track/', views.track_complaint, name='track_complaint'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/super-admin/', views.dashboard_super_admin, name='dashboard_super_admin'),
    path('dashboard/admin/users/', views.admin_users, name='admin_users'),
    path('dashboard/admin/services/', views.admin_services, name='admin_services'),
    path('dashboard/admin/complaints/', views.admin_complaints, name='admin_complaints'),
    path('dashboard/admin/complaints/<int:pk>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('dashboard/admin/users/add/', views.admin_user_add, name='admin_user_add'),
    path('dashboard/admin/users/edit/<int:pk>/', views.admin_user_edit, name='admin_user_edit'),
    path('dashboard/admin/users/delete/<int:pk>/', views.admin_user_delete, name='admin_user_delete'),
    path('dashboard/admin/users/<int:pk>/complaints/', views.admin_user_complaints, name='admin_user_complaints'),
    path('dashboard/admin/services/add/', views.admin_service_add, name='admin_service_add'),
    path('dashboard/admin/services/edit/<int:pk>/', views.admin_service_edit, name='admin_service_edit'),
    path('dashboard/admin/services/delete/<int:pk>/', views.admin_service_delete, name='admin_service_delete'),
    path('dashboard/export_complaints/', views.export_complaints, name='export_complaints'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset_form.html',
        email_template_name='core/password_reset_email.html',
        html_email_template_name='core/password_reset_email_html.html',
        subject_template_name='core/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
]
