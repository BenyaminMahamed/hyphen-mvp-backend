from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ActionItemViewSet, CompletedActionItemListView

router = DefaultRouter()
router.register(r'action-items', ActionItemViewSet, basename='actionitem')

urlpatterns = [
    path('action-items/completed/', CompletedActionItemListView.as_view(), name='completed-action-items'),
] + router.urls