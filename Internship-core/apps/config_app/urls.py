"""系统配置模块路由"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SystemConfigViewSet, AIModelConfigViewSet, upload_image

router = DefaultRouter(trailing_slash=False)
router.register("ai-model", AIModelConfigViewSet, basename="ai-model")
router.register("", SystemConfigViewSet, basename="config")
urlpatterns = [
    path("upload", upload_image, name="config-upload"),
] + router.urls
