"""角色模块视图 — 参考《组织架构模块设计方案.md》第 5.3 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import Role
from .serializers import RoleSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(detail=False, methods=["get"])
    def all(self, request):
        """获取全部角色（下拉框用）"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        return APIResponse.success()

    @action(detail=True, methods=["get", "put"], url_path="menus")
    def menus(self, request, pk=None):
        """获取/分配角色菜单权限"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=True, methods=["get", "put"], url_path="users")
    def users(self, request, pk=None):
        """获取/分配角色下的用户"""
        return APIResponse.success(data={"message": "待实现"})