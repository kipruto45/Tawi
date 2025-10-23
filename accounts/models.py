from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('field_officer', 'Field Officer'),
        # legacy/alternate alias sometimes used in forms
        ('field', 'Field Officer'),
        ('partner', 'Partner Institution'),
        ('partner_institution', 'Partner Institution'),
        ('project_manager', 'Project Manager'),
        ('volunteer', 'Volunteer'),
        ('beneficiary', 'Beneficiary Liaison'),
        ('guest', 'Guest User'),
        ('community', 'Community Representative'),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='volunteer')

    def __str__(self):
        return f"{self.username} ({self.role})"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=32, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    county = models.CharField(max_length=128, blank=True)
    ward = models.CharField(max_length=128, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    @property
    def profile_image(self):
        """Compatibility alias for templates that reference profile_image."""
        if self.profile_picture:
            return self.profile_picture
        return None


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
