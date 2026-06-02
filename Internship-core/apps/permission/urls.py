"""权限模块路由"""
from rest_framework.routers import DefaultRouter
from .views import PermissionViewSet

router = DefaultRouter()
router.register("", PermissionViewSet, basename="permission")
urlpatterns = router.urls