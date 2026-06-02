"""日志模块路由"""
from rest_framework.routers import DefaultRouter
from .views import OperationLogViewSet

router = DefaultRouter()
router.register("", OperationLogViewSet, basename="log")
urlpatterns = router.urls
