from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet, MeetingNoteViewSet

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')
router.register(r'meeting-notes', MeetingNoteViewSet, basename='meetingnote')

urlpatterns = router.urls