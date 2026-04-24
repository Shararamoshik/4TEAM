from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile'
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    description = models.TextField(blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    telegram_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"