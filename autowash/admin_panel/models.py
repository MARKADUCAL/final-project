from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class AdminProfile(models.Model):
    """
    Extended profile for admin users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=100, default='Administrator')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Admin Profile"

class AdminLog(models.Model):
    """
    Log of admin activities
    """
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.timestamp}"

class SiteSettings(models.Model):
    """
    Site-wide settings for the application
    """
    # General Settings
    site_name = models.CharField(max_length=100, default="AutoWash Hub")
    site_description = models.TextField(default="Your premier car wash service provider")
    contact_email = models.EmailField(default="contact@autowashhub.com")
    contact_phone = models.CharField(max_length=20, default="+1 (555) 123-4567")
    business_hours = models.TextField(default="Monday-Friday: 8:00 AM - 6:00 PM\nSaturday: 9:00 AM - 5:00 PM\nSunday: Closed")
    address = models.TextField(default="123 Main Street\nAnytown, ST 12345")
    
    # Appearance Settings
    primary_color = models.CharField(max_length=7, default="#0d6efd")
    secondary_color = models.CharField(max_length=7, default="#6c757d")
    logo = models.ImageField(upload_to='site/', null=True, blank=True)
    favicon = models.ImageField(upload_to='site/', null=True, blank=True)
    enable_dark_mode = models.BooleanField(default=False)
    
    # Booking Settings
    booking_interval = models.IntegerField(default=30, help_text="Booking time interval in minutes")
    min_advance_booking = models.IntegerField(default=2, help_text="Minimum hours in advance for booking")
    max_advance_booking = models.IntegerField(default=30, help_text="Maximum days in advance for booking")
    max_daily_bookings = models.IntegerField(default=20, help_text="Maximum bookings allowed per day")
    allow_same_day_booking = models.BooleanField(default=True)
    require_payment = models.BooleanField(default=False)
    
    # Notification Settings
    notify_new_booking = models.BooleanField(default=True)
    notify_cancelled_booking = models.BooleanField(default=True)
    notify_new_user = models.BooleanField(default=True)
    send_booking_confirmation = models.BooleanField(default=True)
    send_booking_reminder = models.BooleanField(default=True)
    reminder_hours = models.IntegerField(default=24, help_text="Hours before appointment to send reminder")
    
    # Singleton pattern - only one settings instance
    is_active = models.BooleanField(default=True, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one active settings instance exists"""
        if self.is_active:
            # Deactivate all other instances
            SiteSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get the active settings instance or create if none exists"""
        settings = cls.objects.filter(is_active=True).first()
        if not settings:
            settings = cls.objects.create(is_active=True)
        return settings
    
    def __str__(self):
        return f"Site Settings (Last updated: {self.last_updated.strftime('%Y-%m-%d %H:%M')})"

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    """Create AdminProfile when a staff/superuser User is created"""
    if created and (instance.is_staff or instance.is_superuser):
        AdminProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_admin_profile(sender, instance, **kwargs):
    """Save AdminProfile when User is saved"""
    if instance.is_staff or instance.is_superuser:
        if hasattr(instance, 'admin_profile'):
            instance.admin_profile.save()
        else:
            AdminProfile.objects.create(user=instance)
