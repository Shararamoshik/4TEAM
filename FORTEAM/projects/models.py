from django.db import models
from django.conf import settings
import uuid

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_permissions'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='permissions'
    )
    role = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='unique_user_project_permission')
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.project.name} [{self.role}]"

class Invite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='invites'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invites'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Invite to {self.project.name} ({self.token})"