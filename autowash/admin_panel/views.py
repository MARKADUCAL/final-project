from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import AdminProfile, AdminLog, SiteSettings
from authentication.models import UserProfile, Service, Booking
from django.utils import timezone

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
    
    # Get services count
    services_count = Service.objects.count()
    
    # Get active bookings count
    active_bookings = Booking.objects.filter(status='PENDING').count()
    
    # Calculate revenue (this month)
    current_month = timezone.now().month
    current_year = timezone.now().year
    completed_bookings = Booking.objects.filter(
        status='COMPLETED',
        date_time__month=current_month,
        date_time__year=current_year
    )
    
    # Calculate total revenue from completed bookings
    revenue = 0
    for booking in completed_bookings:
        if booking.service and booking.service.price:
            revenue += float(booking.service.price)
    
    # Get recent admin logs
    recent_logs = AdminLog.objects.all().order_by('-timestamp')[:10]
    
    # Get site settings
    site_settings = SiteSettings.get_settings()
    
    context = {
        'total_users': total_users,
        'recent_logs': recent_logs,
        'active_bookings': active_bookings,
        'revenue': revenue,
        'services_count': services_count,
        'site_settings': site_settings
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

@login_required
@user_passes_test(is_admin)
def user_details(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    user_profile = UserProfile.objects.get(user=user)
    
    # Log the action
    AdminLog.objects.create(
        admin=request.user,
        action="View User Details",
        ip_address=get_client_ip(request),
        details=f"Admin viewed details of user {user.username} (ID: {user_id})"
    )
    
    context = {
        'user_obj': user,
        'user_profile': user_profile
    }
    
    return render(request, 'admin_panel/user_details.html', context)

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    """Edit user"""
    user = get_object_or_404(User, id=user_id)
    user_profile = UserProfile.objects.get(user=user)
    
    if request.method == 'POST':
        # Update user data
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = 'is_active' in request.POST
        
        # Update profile data if needed
        if 'phone_number' in request.POST:
            user_profile.phone_number = request.POST.get('phone_number')
            user_profile.save()
            
        user.save()
        
        # Log the action
        AdminLog.objects.create(
            admin=request.user,
            action="Edit User",
            ip_address=get_client_ip(request),
            details=f"Admin edited user {user.username} (ID: {user_id})"
        )
        
        messages.success(request, f"User {user.username} has been updated successfully")
        return redirect('admin_users')
    
    context = {
        'user_obj': user,
        'user_profile': user_profile
    }
    
    return render(request, 'admin_panel/edit_user.html', context)

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    username = user.username
    
    if request.method == 'POST':
        # Log the action before deletion
        AdminLog.objects.create(
            admin=request.user,
            action="Delete User",
            ip_address=get_client_ip(request),
            details=f"Admin deleted user {username} (ID: {user_id})"
        )
        
        user.delete()
        messages.success(request, f"User {username} has been deleted successfully")
        return redirect('admin_users')
    
    context = {
        'user_obj': user
    }
    
    return render(request, 'admin_panel/delete_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_services(request):
    """View to list all services"""
    services = Service.objects.all().order_by('name')
    
    # Log the action
    AdminLog.objects.create(
        admin=request.user,
        action="View Services",
        ip_address=get_client_ip(request),
        details="Admin viewed services list"
    )
    
    context = {
        'services': services,
        'total_services': services.count()
    }
    
    return render(request, 'admin_panel/services.html', context)

@login_required
@user_passes_test(is_admin)
def add_service(request):
    """Add a new service"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_minutes = request.POST.get('duration_minutes')
        
        # Validate inputs
        if not all([name, description, price, duration_minutes]):
            messages.error(request, "All fields are required")
            return redirect('add_service')
        
        try:
            # Create new service
            service = Service.objects.create(
                name=name,
                description=description,
                price=price,
                duration_minutes=duration_minutes
            )
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Add Service",
                ip_address=get_client_ip(request),
                details=f"Admin added new service: {name}"
            )
            
            messages.success(request, f"Service '{name}' has been added successfully")
            return redirect('admin_services')
        except Exception as e:
            messages.error(request, f"Error adding service: {str(e)}")
            return redirect('add_service')
    
    return render(request, 'admin_panel/add_service.html')

@login_required
@user_passes_test(is_admin)
def edit_service(request, service_id):
    """Edit a service"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.duration_minutes = request.POST.get('duration_minutes')
        
        try:
            service.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Edit Service",
                ip_address=get_client_ip(request),
                details=f"Admin edited service: {service.name} (ID: {service_id})"
            )
            
            messages.success(request, f"Service '{service.name}' has been updated successfully")
            return redirect('admin_services')
        except Exception as e:
            messages.error(request, f"Error updating service: {str(e)}")
    
    context = {
        'service': service
    }
    
    return render(request, 'admin_panel/edit_service.html', context)

@login_required
@user_passes_test(is_admin)
def delete_service(request, service_id):
    """Delete a service"""
    service = get_object_or_404(Service, id=service_id)
    service_name = service.name
    
    if request.method == 'POST':
        try:
            # Log the action before deletion
            AdminLog.objects.create(
                admin=request.user,
                action="Delete Service",
                ip_address=get_client_ip(request),
                details=f"Admin deleted service: {service_name} (ID: {service_id})"
            )
            
            service.delete()
            messages.success(request, f"Service '{service_name}' has been deleted successfully")
            return redirect('admin_services')
        except Exception as e:
            messages.error(request, f"Error deleting service: {str(e)}")
            return redirect('admin_services')
    
    context = {
        'service': service
    }
    
    return render(request, 'admin_panel/delete_service.html', context)

@login_required
@user_passes_test(is_admin)
def admin_bookings(request):
    """View to list all bookings"""
    # Get filter parameters from query string
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    # Start with all bookings
    bookings = Booking.objects.all().order_by('-date_time')
    
    # Apply filters if provided
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    if date_filter:
        try:
            date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            bookings = bookings.filter(date_time__date=date)
        except ValueError:
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
    
    # Log the action
    AdminLog.objects.create(
        admin=request.user,
        action="View Bookings",
        ip_address=get_client_ip(request),
        details="Admin viewed bookings list"
    )
    
    context = {
        'bookings': bookings,
        'total_bookings': bookings.count(),
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Booking.STATUS_CHOICES
    }
    
    return render(request, 'admin_panel/bookings.html', context)

@login_required
@user_passes_test(is_admin)
def booking_details(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Log the action
    AdminLog.objects.create(
        admin=request.user,
        action="View Booking Details",
        ip_address=get_client_ip(request),
        details=f"Admin viewed details of booking {booking.booking_id}"
    )
    
    context = {
        'booking': booking
    }
    
    return render(request, 'admin_panel/booking_details.html', context)

@login_required
@user_passes_test(is_admin)
def update_booking_status(request, booking_id):
    """Update booking status"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        # Accept both uppercase and lowercase status values
        if new_status in ['pending', 'completed', 'cancelled', 'PENDING', 'COMPLETED', 'CANCELLED']:
            old_status = booking.status
            booking.status = new_status.upper()  # Convert to uppercase to match model definition
            booking.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Booking Status",
                ip_address=get_client_ip(request),
                details=f"Admin updated booking #{booking_id} status from {old_status} to {booking.status}"
            )
            
            messages.success(request, f"Booking status updated to {booking.status.lower()}")
        else:
            messages.error(request, "Invalid status")
    
    return redirect('booking_details', booking_id=booking_id)

@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings view"""
    # Get or create settings
    settings = SiteSettings.get_settings()
    
    if request.method == 'POST':
        setting_type = request.POST.get('setting_type')
        
        # Handle different types of settings
        if setting_type == 'general':
            # Process general settings
            settings.site_name = request.POST.get('site_name')
            settings.site_description = request.POST.get('site_description')
            settings.contact_email = request.POST.get('contact_email')
            settings.contact_phone = request.POST.get('contact_phone')
            settings.business_hours = request.POST.get('business_hours')
            settings.address = request.POST.get('address')
            
            # Save settings
            settings.updated_by = request.user
            settings.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Settings",
                ip_address=get_client_ip(request),
                details=f"Admin updated general settings"
            )
            
            messages.success(request, "General settings updated successfully")
            
        elif setting_type == 'appearance':
            # Process appearance settings
            settings.primary_color = f"#{request.POST.get('primary_color')}"
            settings.secondary_color = f"#{request.POST.get('secondary_color')}"
            settings.enable_dark_mode = 'enable_dark_mode' in request.POST
            
            # Handle file uploads if present
            if 'logo' in request.FILES:
                settings.logo = request.FILES['logo']
            
            if 'favicon' in request.FILES:
                settings.favicon = request.FILES['favicon']
            
            # Save settings
            settings.updated_by = request.user
            settings.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Settings",
                ip_address=get_client_ip(request),
                details=f"Admin updated appearance settings"
            )
            
            messages.success(request, "Appearance settings updated successfully")
            
        elif setting_type == 'booking':
            # Process booking settings
            settings.booking_interval = request.POST.get('booking_interval')
            settings.min_advance_booking = request.POST.get('min_advance_booking')
            settings.max_advance_booking = request.POST.get('max_advance_booking')
            settings.max_daily_bookings = request.POST.get('max_daily_bookings')
            settings.allow_same_day_booking = 'allow_same_day_booking' in request.POST
            settings.require_payment = 'require_payment' in request.POST
            
            # Save settings
            settings.updated_by = request.user
            settings.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Settings",
                ip_address=get_client_ip(request),
                details=f"Admin updated booking settings"
            )
            
            messages.success(request, "Booking settings updated successfully")
            
        elif setting_type == 'notifications':
            # Process notification settings
            settings.notify_new_booking = 'notify_new_booking' in request.POST
            settings.notify_cancelled_booking = 'notify_cancelled_booking' in request.POST
            settings.notify_new_user = 'notify_new_user' in request.POST
            settings.send_booking_confirmation = 'send_booking_confirmation' in request.POST
            settings.send_booking_reminder = 'send_booking_reminder' in request.POST
            settings.reminder_hours = request.POST.get('reminder_hours')
            
            # Save settings
            settings.updated_by = request.user
            settings.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Settings",
                ip_address=get_client_ip(request),
                details=f"Admin updated notification settings"
            )
            
            messages.success(request, "Notification settings updated successfully")
            
        elif setting_type == 'account':
            # Process account settings
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            position = request.POST.get('position')
            
            # Update user information
            user = request.user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            # Update admin profile if exists
            if hasattr(user, 'admin_profile'):
                admin_profile = user.admin_profile
                admin_profile.position = position
                admin_profile.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Update Profile",
                ip_address=get_client_ip(request),
                details=f"Admin updated their profile information"
            )
            
            messages.success(request, "Your profile has been updated successfully")
            
        elif setting_type == 'security':
            # Process security settings - password change
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate inputs
            if not all([current_password, new_password, confirm_password]):
                messages.error(request, "All password fields are required")
                return redirect('admin_settings')
                
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return redirect('admin_settings')
                
            # Check current password
            user = request.user
            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")
                return redirect('admin_settings')
                
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Log the action
            AdminLog.objects.create(
                admin=request.user,
                action="Change Password",
                ip_address=get_client_ip(request),
                details=f"Admin changed their password"
            )
            
            messages.success(request, "Your password has been changed successfully. Please log in again.")
            return redirect('admin_logout')
    
    # Log the action for viewing settings
    AdminLog.objects.create(
        admin=request.user,
        action="View Settings",
        ip_address=get_client_ip(request),
        details="Admin viewed settings page"
    )
    
    # Pass settings to the template
    context = {
        'settings': settings,
        'now': timezone.now(),
    }
    
    return render(request, 'admin_panel/setting.html', context)
