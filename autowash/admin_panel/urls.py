from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_login, name='admin_panel_root'),
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('users/', views.admin_users, name='admin_users'),
    path('users/<int:user_id>/', views.user_details, name='user_details'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('services/', views.admin_services, name='admin_services'),
    path('services/add/', views.add_service, name='add_service'),
    path('services/<int:service_id>/edit/', views.edit_service, name='edit_service'),
    path('services/<int:service_id>/delete/', views.delete_service, name='delete_service'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),
    path('bookings/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('bookings/<int:booking_id>/update-status/', views.update_booking_status, name='update_booking_status'),
    path('settings/', views.admin_settings, name='admin_settings'),
] 