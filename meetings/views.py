from rest_framework import viewsets, permissions
from .models import Meeting
from .serializers import MeetingSerializer


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