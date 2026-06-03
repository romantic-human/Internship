"""权限模块视图 — 参考《组织架构模块设计方案.md》第 5.5 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import Permission
from .serializers import PermissionSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    @action(detail=True, methods=["get", "put"], url_path="menus")
    def menus(self, request, pk=None):
        """获取/绑定权限到菜单"""
        return APIResponse.success(data={"message": "待实现"})