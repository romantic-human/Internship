"""数据字典模块路由"""
from rest_framework.routers import DefaultRouter
from .views import DictTypeViewSet, DictDataViewSet

router = DefaultRouter(trailing_slash=False)
router.register("type", DictTypeViewSet, basename="dict-type")
router.register("data", DictDataViewSet, basename="dict-data")
urlpatterns = router.urls
