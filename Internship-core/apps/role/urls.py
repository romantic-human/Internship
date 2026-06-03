"""角色模块路由"""
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", RoleViewSet, basename="role")
urlpatterns = router.urls