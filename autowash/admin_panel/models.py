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
