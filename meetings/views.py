from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Meeting, MeetingNote
from .serializers import MeetingSerializer, MeetingNoteSerializer
from core.permissions import IsManager


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == "manager":
            return Meeting.objects.all()
        return Meeting.objects.filter(teams=user.profile.team)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        from actions.models import ActionItem
        if ActionItem.objects.filter(note__meeting=instance, status="open").exists():
            raise PermissionDenied("Cannot delete a meeting with open action items.")
        instance.delete()


class MeetingNoteViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingNoteSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == "manager":
            return MeetingNote.objects.all()
        return MeetingNote.objects.filter(meeting__teams=user.profile.team)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsManager()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        from ai_integration.services import generate_summary_and_actions
        from actions.models import ActionItem

        note = serializer.save(submitted_by=self.request.user)
        result = generate_summary_and_actions(note.raw_text)

        note.ai_summary = result["summary"]
        note.save()

        for description in result["action_items"]:
            ActionItem.objects.create(
                note=note,
                description=description,
                owner=self.request.user,
                created_from_ai=True,
            )