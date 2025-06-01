from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AdminProfile, AdminLog
from authentication.models import UserProfile

# Create your views here.

def is_admin(user):
    """Check if the user is staff or superuser"""
    return user.is_staff or user.is_superuser

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def admin_login(request):
    """Admin login view"""
    # If user is already logged in and is admin, redirect to admin dashboard
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            
            # Log the login activity
            ip_address = get_client_ip(request)
            AdminLog.objects.create(
                admin=user,
                action="Login",
                ip_address=ip_address,
                details=f"Admin login from {ip_address}"
            )
            
            # Update last login IP
            if hasattr(user, 'admin_profile'):
                user.admin_profile.last_login_ip = ip_address
                user.admin_profile.save()
            
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials or insufficient permissions')
            
    return render(request, 'admin_panel/login.html')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Get total users count
    total_users = User.objects.count()
    
    # Get recent admin logs
    recent_logs = AdminLog.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'recent_logs': recent_logs,
        # These are placeholders - you would replace with actual data
        'active_bookings': 0,
        'revenue': 0,
        'services_count': 0
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    """Admin logout view"""
    # Log the logout activity
    AdminLog.objects.create(
        admin=request.user,
        action="Logout",
        ip_address=get_client_ip(request),
        details="Admin logout"
    )
    
    logout(request)
    messages.success(request, 'You have been logged out from the admin panel')
    return redirect('admin_login')

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """View to list all customer users"""
    # Get all users with customer profile
    customer_profiles = UserProfile.objects.filter(user_type='customer')
    customer_users = [profile.user for profile in customer_profiles]
    
    # Log the action
    AdminLog.objects.create(
        admin=request.user,
        action="View Customers",
        ip_address=get_client_ip(request),
        details="Admin viewed customer list"
    )
    
    context = {
        'customers': customer_users,
        'total_customers': len(customer_users)
    }
    
    return render(request, 'admin_panel/users.html', context)
