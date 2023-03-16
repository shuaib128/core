from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Additional fields for the profile model
    username = models.CharField(max_length=200, default="username")
    bio = models.TextField(max_length=500, blank=True)
    email = models.EmailField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        default='default_profile_picture.png'
    )

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        self.email = self.user.email
        self.username = self.user.username
        super().save(*args, **kwargs)