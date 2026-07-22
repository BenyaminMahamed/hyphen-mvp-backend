from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from core.models import Team, Profile
from meetings.models import Meeting, MeetingNote
from .models import ActionItem


class ActionItemBusinessRulesTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name="Operations")

        self.manager_user = User.objects.create_user(username="manager1", password="testpass123")
        Profile.objects.create(user=self.manager_user, team=self.team, role="manager")

        self.member_user = User.objects.create_user(username="member1", password="testpass123")
        Profile.objects.create(user=self.member_user, team=self.team, role="member")

        self.meeting = Meeting.objects.create(title="Test Meeting", date="2026-07-20", created_by=self.manager_user)
        self.meeting.teams.add(self.team)

        self.note = MeetingNote.objects.create(meeting=self.meeting, submitted_by=self.manager_user, raw_text="Test notes.")

        self.action_item = ActionItem.objects.create(
            note=self.note, description="Test action", owner=self.member_user, status="open"
        )

        self.manager_client = APIClient()
        manager_token = Token.objects.create(user=self.manager_user)
        self.manager_client.credentials(HTTP_AUTHORIZATION=f"Token {manager_token.key}")

        self.member_client = APIClient()
        member_token = Token.objects.create(user=self.member_user)
        self.member_client.credentials(HTTP_AUTHORIZATION=f"Token {member_token.key}")

    def test_completed_action_item_cannot_be_edited(self):
        self.action_item.status = "completed"
        self.action_item.save()

        response = self.manager_client.patch(
            f"/api/action-items/{self.action_item.id}/",
            {"description": "Changed description"},
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_can_reassign_completed_action_item(self):
        self.action_item.status = "completed"
        self.action_item.save()

        response = self.manager_client.patch(
            f"/api/action-items/{self.action_item.id}/",
            {"owner": self.manager_user.id},
        )
        self.assertEqual(response.status_code, 200)

    def test_member_cannot_reassign_completed_action_item(self):
        self.action_item.status = "completed"
        self.action_item.save()

        # Genuine reassignment attempt: member owns it, tries to hand it to the manager.
        response = self.member_client.patch(
            f"/api/action-items/{self.action_item.id}/",
            {"owner": self.manager_user.id},
        )
        self.assertEqual(response.status_code, 403)

    def test_meeting_cannot_be_deleted_with_open_action_items(self):
        response = self.manager_client.delete(f"/api/meetings/{self.meeting.id}/")
        self.assertEqual(response.status_code, 403)

    def test_meeting_can_be_deleted_once_action_items_completed(self):
        self.action_item.status = "completed"
        self.action_item.save()

        response = self.manager_client.delete(f"/api/meetings/{self.meeting.id}/")
        self.assertEqual(response.status_code, 204)

    def test_completed_action_appears_in_outgoing_feed(self):
        self.action_item.status = "completed"
        self.action_item.save()

        response = self.manager_client.get("/api/action-items/completed/")
        self.assertEqual(response.status_code, 200)
        ids = [item["id"] for item in response.data]
        self.assertIn(self.action_item.id, ids)