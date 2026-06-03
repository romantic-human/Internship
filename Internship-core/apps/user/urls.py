"""用户模块路由"""
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", UserViewSet, basename="user")
urlpatterns = router.urls