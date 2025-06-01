from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('booking/', views.booking_view, name='booking'),
    path('mybookings/', views.mybookings_view, name='mybookings'),
    path('booking/reschedule/<int:booking_id>/', views.reschedule_booking, name='reschedule_booking'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/book-again/<int:booking_id>/', views.book_again, name='book_again'),
    path('booking/receipt/<int:booking_id>/', views.view_receipt, name='view_receipt'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/token/', views.api_get_token, name='api_get_token'),
    path('api/auth-status/', views.api_auth_status, name='api_auth_status'),
    path('api/services/', views.api_get_services, name='api_get_services'),
    path('api/bookings/', views.api_get_bookings, name='api_get_bookings'),
    path('api/bookings/create/', views.api_create_booking, name='api_create_booking'),
    path('api/bookings/<int:booking_id>/', views.api_booking_detail, name='api_booking_detail'),
] 