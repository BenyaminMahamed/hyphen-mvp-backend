from rest_framework import serializers
from .models import ActionItem


class ActionItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = ActionItem
        fields = ['id', 'note', 'description', 'owner', 'owner_username', 'status', 'created_from_ai', 'created_at', 'completed_at']
        read_only_fields = ['created_from_ai', 'created_at', 'completed_at']
