"""系统配置模块路由"""
from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", SystemConfigViewSet, basename="config")
urlpatterns = router.urls