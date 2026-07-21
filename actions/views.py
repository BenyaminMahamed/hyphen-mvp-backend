from rest_framework import viewsets, permissions
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

        if instance.status == "completed":
            raise PermissionDenied("Completed action items cannot be edited.")

        new_owner = serializer.validated_data.get("owner", instance.owner)
        if new_owner != instance.owner and instance.status == "completed" and user.profile.role != "manager":
            raise PermissionDenied("Only managers can reassign completed actions.")

        serializer.save()