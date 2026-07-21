from django.utils import timezone
from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied
from .models import ActionItem
from .serializers import ActionItemSerializer


class ActionItemViewSet(viewsets.ModelViewSet):
    serializer_class = ActionItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == "manager":
            return ActionItem.objects.all()
        return ActionItem.objects.filter(note__meeting__teams=user.profile.team)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user

        new_owner = serializer.validated_data.get("owner", instance.owner)
        new_status = serializer.validated_data.get("status", instance.status)
        is_reassignment = new_owner != instance.owner
        other_fields_changed = any(
            key != "owner" and getattr(instance, key) != value
            for key, value in serializer.validated_data.items()
        )

        if instance.status == "completed":
            if other_fields_changed:
                raise PermissionDenied("Completed action items cannot be edited.")
            if is_reassignment and user.profile.role != "manager":
                raise PermissionDenied("Only managers can reassign completed actions.")

        if new_status == "completed" and instance.status != "completed":
            serializer.save(completed_at=timezone.now())
        elif new_status != "completed" and instance.status == "completed":
            serializer.save(completed_at=None)
        else:
            serializer.save()


class CompletedActionItemListView(generics.ListAPIView):
    """
    Outgoing API for another internal system to retrieve completed action items.
    No manager/member visibility filtering — this is a system-to-system feed,
    not a user-facing endpoint, so it returns all completed items.
    """
    serializer_class = ActionItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ActionItem.objects.filter(status="completed")