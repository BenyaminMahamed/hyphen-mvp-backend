from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = [
        ("member", "Team Member"),
        ("manager", "Team Manager"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="members")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")

    def __str__(self):
        return f"{self.user.username} ({self.role})"