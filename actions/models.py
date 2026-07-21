from django.db import models
from django.contrib.auth.models import User
from meetings.models import MeetingNote


class ActionItem(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("completed", "Completed"),
    ]

    note = models.ForeignKey(MeetingNote, on_delete=models.CASCADE, related_name="action_items")
    description = models.CharField(max_length=300)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name="action_items")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="open")
    created_from_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.description} ({self.status})"