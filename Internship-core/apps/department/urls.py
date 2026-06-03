"""部门模块路由"""
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet

router = DefaultRouter()
router.register("", DepartmentViewSet, basename="department")
urlpatterns = router.urls