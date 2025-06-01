from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Booking, Service, UserProfile
from datetime import datetime, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.tokens import default_token_generator

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Replace with your home/dashboard URL
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'authentication/login.html')

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'status': 'success',
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid username or password'
                }, status=401)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login')
        
    return render(request, 'authentication/register.html')

@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            username = data.get('username')
            email = data.get('email')
            password1 = data.get('password')
            password2 = data.get('confirm_password')
            
            # Validation
            if not all([first_name, last_name, username, email, password1, password2]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required'
                }, status=400)
                
            if password1 != password2:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Passwords do not match'
                }, status=400)
                
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username already exists'
                }, status=400)
                
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already exists'
                }, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Account created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')

@login_required
def dashboard_view(request):
    # Get upcoming bookings for the user (pending bookings with future dates)
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        status='PENDING',
        date_time__gte=datetime.now()
    ).order_by('date_time')[:3]  # Limit to 3 most recent bookings
    
    # Get all available services
    services = Service.objects.all()
    
    return render(request, 'dashboard/index.html', {
        'upcoming_bookings': upcoming_bookings,
        'services': services
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Check which form was submitted
        if 'first_name' in request.POST:
            # Profile update form
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            
            # Update user
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            # Update or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = phone
            profile.address = address
            profile.save()
            
            messages.success(request, 'Profile updated successfully')
            
        elif 'current_password' in request.POST:
            # Password change form
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            else:
                # Change password
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password changed successfully. Please log in again.')
                return redirect('login')
                
        elif 'profile_picture' in request.FILES:
            # Profile picture update
            profile_picture = request.FILES.get('profile_picture')
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.profile_picture = profile_picture
            profile.save()
            messages.success(request, 'Profile picture updated successfully')
            
    # Get total bookings count
    bookings_count = Booking.objects.filter(user=request.user).count()
    
    # Format dates for template
    member_since = request.user.date_joined.strftime("%B %d, %Y")
    last_login = request.user.last_login.strftime("%B %d, %Y") if request.user.last_login else "Never"
            
    return render(request, 'dashboard/profile.html', {
        'bookings_count': bookings_count,
        'member_since': member_since,
        'last_login': last_login
    })

@login_required
def booking_view(request):
    services = Service.objects.all()
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        date = request.POST.get('date')
        time = request.POST.get('time')
        vehicle_make = request.POST.get('vehicle_make')
        vehicle_model = request.POST.get('vehicle_model')
        vehicle_type = request.POST.get('vehicle_type')
        license_plate = request.POST.get('license_plate')
        notes = request.POST.get('notes')
        
        # Validate inputs
        if not all([service_id, date, time, vehicle_make, vehicle_model, vehicle_type, license_plate]):
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'dashboard/booking.html', {'services': services})
        
        try:
            service = Service.objects.get(id=service_id)
            date_time_str = f"{date} {time}"
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            
            # Create booking
            booking = Booking(
                user=request.user,
                service=service,
                date_time=date_time,
                vehicle_make=vehicle_make,
                vehicle_model=vehicle_model,
                vehicle_type=vehicle_type,
                license_plate=license_plate,
                additional_notes=notes
            )
            booking.save()
            
            messages.success(request, f'Your {service.name} booking has been confirmed for {date_time.strftime("%B %d, %Y at %I:%M %p")}')
            return redirect('mybookings')
            
        except Service.DoesNotExist:
            messages.error(request, 'Invalid service selected')
        except ValueError:
            messages.error(request, 'Invalid date or time format')
    
    return render(request, 'dashboard/booking.html', {'services': services})

@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'PENDING':
        messages.error(request, 'Only pending bookings can be rescheduled')
        return redirect('mybookings')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        try:
            date_time_str = f"{date} {time}"
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            
            booking.date_time = date_time
            booking.save()
            
            messages.success(request, f'Your booking has been rescheduled to {date_time.strftime("%B %d, %Y at %I:%M %p")}')
            return redirect('mybookings')
            
        except ValueError:
            messages.error(request, 'Invalid date or time format')
    
    return render(request, 'dashboard/reschedule.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'PENDING':
        messages.error(request, 'Only pending bookings can be cancelled')
        return redirect('mybookings')
    
    if request.method == 'POST':
        booking.status = 'CANCELLED'
        booking.save()
        
        messages.success(request, 'Your booking has been cancelled')
        return redirect('mybookings')
    
    return render(request, 'dashboard/cancel_booking.html', {'booking': booking})

@login_required
def book_again(request, booking_id):
    original_booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Create a new pending booking with the same details
    new_booking = Booking(
        user=request.user,
        service=original_booking.service,
        date_time=datetime.now() + timedelta(days=1),  # Schedule for tomorrow
        vehicle_make=original_booking.vehicle_make,
        vehicle_model=original_booking.vehicle_model,
        vehicle_type=original_booking.vehicle_type,
        license_plate=original_booking.license_plate,
        additional_notes=original_booking.additional_notes
    )
    new_booking.save()
    
    messages.success(request, f'Your {new_booking.service.name} booking has been created. Please update the date and time.')
    return redirect('reschedule_booking', booking_id=new_booking.id)

@login_required
def view_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status != 'COMPLETED':
        messages.error(request, 'Receipt is only available for completed bookings')
        return redirect('mybookings')
    
    return render(request, 'dashboard/receipt.html', {'booking': booking})

@login_required
def mybookings_view(request):
    # Get all bookings for the current user
    bookings = Booking.objects.filter(user=request.user).order_by('-date_time')
    
    return render(request, 'dashboard/mybooking.html', {
        'bookings': bookings
    })

# API Endpoints for Bookings
@csrf_exempt
def api_get_services(request):
    """API endpoint to get all available services"""
    if request.method == 'GET':
        services = Service.objects.all()
        services_data = []
        
        for service in services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'price': float(service.price),
                'duration_minutes': service.duration_minutes
            })
        
        return JsonResponse({
            'status': 'success',
            'services': services_data
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only GET method is allowed'
    }, status=405)

@csrf_exempt
def api_create_booking(request):
    """API endpoint to create a new booking"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check for test_mode parameter
            test_mode = data.get('test_mode', False)
            
            # Get user from token or session
            user = get_user_from_request(request)
            
            # If test_mode is True and no user is authenticated, use the first available user
            if test_mode and user is None:
                try:
                    user = User.objects.first()
                    if user is None:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'No users available for test mode'
                        }, status=400)
                except:
                    pass
            
            # Check if user is authenticated
            if user is None:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required'
                }, status=401)
            
            service_id = data.get('service_id')
            date_time_str = data.get('date_time')
            vehicle_make = data.get('vehicle_make')
            vehicle_model = data.get('vehicle_model')
            vehicle_type = data.get('vehicle_type')
            license_plate = data.get('license_plate')
            additional_notes = data.get('additional_notes', '')
            
            # Validate inputs
            if not all([service_id, date_time_str, vehicle_make, vehicle_model, vehicle_type, license_plate]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields'
                }, status=400)
            
            try:
                service = Service.objects.get(id=service_id)
                date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                
                # Create booking
                booking = Booking(
                    user=user,
                    service=service,
                    date_time=date_time,
                    vehicle_make=vehicle_make,
                    vehicle_model=vehicle_model,
                    vehicle_type=vehicle_type,
                    license_plate=license_plate,
                    additional_notes=additional_notes
                )
                booking.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Booking created successfully',
                    'booking': {
                        'id': booking.id,
                        'booking_id': booking.booking_id,
                        'service': booking.service.name,
                        'date_time': booking.date_time.strftime('%Y-%m-%d %H:%M'),
                        'status': booking.status,
                        'price': float(booking.service.price)
                    }
                })
                
            except Service.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid service selected'
                }, status=400)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid date or time format. Use YYYY-MM-DD HH:MM format.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)

def get_user_from_request(request):
    """Helper function to get user from request using token or session"""
    # Try to get token from multiple sources
    token = None
    
    # 1. Check Authorization header
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Token '):
        token = auth_header.split(' ')[1]
    
    # 2. Check query parameters
    if not token and request.GET.get('token'):
        token = request.GET.get('token')
    
    # 3. Check request body for token
    if not token and request.method == 'POST':
        try:
            if hasattr(request, 'body') and request.body:
                body_data = json.loads(request.body)
                if 'token' in body_data:
                    token = body_data.get('token')
        except:
            pass
    
    # Authenticate user with token or session
    user = None
    if token:
        # Try to get user from token
        try:
            # Simple token implementation - in production use Django REST framework TokenAuthentication
            for u in User.objects.all():
                if default_token_generator.check_token(u, token):
                    user = u
                    break
        except Exception as e:
            pass
    
    # Fall back to session authentication
    if user is None and request.user.is_authenticated:
        user = request.user
    
    return user

@csrf_exempt
def api_get_bookings(request):
    """API endpoint to get user's bookings"""
    if request.method == 'GET':
        user = get_user_from_request(request)
        
        if user is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        bookings = Booking.objects.filter(user=user).order_by('-date_time')
        bookings_data = []
        
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'booking_id': booking.booking_id,
                'service': booking.service.name,
                'service_id': booking.service.id,
                'date_time': booking.date_time.strftime('%Y-%m-%d %H:%M'),
                'status': booking.status,
                'vehicle_make': booking.vehicle_make,
                'vehicle_model': booking.vehicle_model,
                'vehicle_type': booking.vehicle_type,
                'license_plate': booking.license_plate,
                'additional_notes': booking.additional_notes,
                'price': float(booking.service.price),
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': booking.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'status': 'success',
            'bookings': bookings_data
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only GET method is allowed'
    }, status=405)

@csrf_exempt
def api_booking_detail(request, booking_id):
    """API endpoint to get, update or cancel a specific booking"""
    user = get_user_from_request(request)
    
    if user is None:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required'
        }, status=401)
    
    try:
        booking = Booking.objects.get(id=booking_id, user=user)
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Booking not found'
        }, status=404)
    
    # GET - Retrieve booking details
    if request.method == 'GET':
        booking_data = {
            'id': booking.id,
            'booking_id': booking.booking_id,
            'service': booking.service.name,
            'service_id': booking.service.id,
            'date_time': booking.date_time.strftime('%Y-%m-%d %H:%M'),
            'status': booking.status,
            'vehicle_make': booking.vehicle_make,
            'vehicle_model': booking.vehicle_model,
            'vehicle_type': booking.vehicle_type,
            'license_plate': booking.license_plate,
            'additional_notes': booking.additional_notes,
            'price': float(booking.service.price),
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': booking.updated_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return JsonResponse({
            'status': 'success',
            'booking': booking_data
        })
    
    # PUT - Update booking (reschedule)
    elif request.method == 'PUT':
        if booking.status != 'PENDING':
            return JsonResponse({
                'status': 'error',
                'message': 'Only pending bookings can be updated'
            }, status=400)
        
        try:
            data = json.loads(request.body)
            date_time_str = data.get('date_time')
            
            if not date_time_str:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing date_time field'
                }, status=400)
            
            try:
                date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
                booking.date_time = date_time
                booking.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Booking rescheduled successfully',
                    'booking': {
                        'id': booking.id,
                        'booking_id': booking.booking_id,
                        'date_time': booking.date_time.strftime('%Y-%m-%d %H:%M'),
                        'status': booking.status
                    }
                })
                
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid date or time format. Use YYYY-MM-DD HH:MM format.'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    # DELETE - Cancel booking
    elif request.method == 'DELETE':
        if booking.status != 'PENDING':
            return JsonResponse({
                'status': 'error',
                'message': 'Only pending bookings can be cancelled'
            }, status=400)
        
        booking.status = 'CANCELLED'
        booking.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Booking cancelled successfully'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@csrf_exempt
def api_get_token(request):
    """API endpoint to get an authentication token"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not all([username, password]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Username and password are required'
                }, status=400)
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Generate token
                token = default_token_generator.make_token(user)
                
                return JsonResponse({
                    'status': 'success',
                    'token': token,
                    'user_id': user.id,
                    'username': user.username
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials'
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method is allowed'
    }, status=405)

@csrf_exempt
def api_auth_status(request):
    """Debug endpoint to check authentication status"""
    user = get_user_from_request(request)
    
    if user:
        return JsonResponse({
            'status': 'success',
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'headers': dict(request.headers),
            'method': request.method,
            'path': request.path
        })
    else:
        return JsonResponse({
            'status': 'error',
            'authenticated': False,
            'headers': dict(request.headers),
            'method': request.method,
            'path': request.path
        }, status=401)
