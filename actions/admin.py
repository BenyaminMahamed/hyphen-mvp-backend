from django.contrib import admin
from .models import ActionItem


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ("description", "owner", "status", "created_from_ai", "completed_at")
    list_filter = ("status", "created_from_ai")