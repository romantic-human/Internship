"""通知模块路由"""
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", NotificationViewSet, basename="notification")
urlpatterns = router.urls
