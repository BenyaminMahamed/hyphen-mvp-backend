from django.contrib import admin
from .models import Meeting, MeetingNote


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "created_by")
    filter_horizontal = ("teams",)


@admin.register(MeetingNote)
class MeetingNoteAdmin(admin.ModelAdmin):
    list_display = ("meeting", "submitted_by", "created_at")