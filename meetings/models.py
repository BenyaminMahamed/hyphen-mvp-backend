from django.db import models
from django.contrib.auth.models import User
from core.models import Team


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    teams = models.ManyToManyField(Team, related_name="meetings")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="meetings_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.date})"


class MeetingNote(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="notes")
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="notes_submitted")
    raw_text = models.TextField()
    ai_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note on {self.meeting.title} by {self.submitted_by.username}"