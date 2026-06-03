"""菜单模块路由"""
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet

router = DefaultRouter(trailing_slash=False)
router.register("", MenuViewSet, basename="menu")
urlpatterns = router.urls