"""学生模块路由"""
from rest_framework.routers import DefaultRouter
from .views import StudentInfoViewSet, StudentScoreViewSet

router = DefaultRouter(trailing_slash=False)
router.register("info", StudentInfoViewSet, basename="student-info")
router.register("score", StudentScoreViewSet, basename="student-score")
urlpatterns = router.urls
