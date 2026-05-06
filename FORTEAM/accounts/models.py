from django.db import models
from django.contrib.auth.models import AbstractUser


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

import uuid

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification_token'
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.username}"