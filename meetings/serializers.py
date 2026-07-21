from rest_framework import serializers
from .models import Meeting, MeetingNote


class MeetingNoteSerializer(serializers.ModelSerializer):
    submitted_by = serializers.ReadOnlyField(source='submitted_by.username')

    class Meta:
        model = MeetingNote
        fields = ['id', 'meeting', 'submitted_by', 'raw_text', 'ai_summary', 'created_at']
        read_only_fields = ['ai_summary', 'created_at']


class MeetingSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    notes = MeetingNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'date', 'teams', 'created_by', 'notes', 'created_at']
        read_only_fields = ['created_at']
