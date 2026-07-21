from rest_framework.routers import DefaultRouter
from .views import ActionItemViewSet

router = DefaultRouter()
router.register(r'action-items', ActionItemViewSet, basename='actionitem')

urlpatterns = router.urls
