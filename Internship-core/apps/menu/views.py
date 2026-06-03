"""菜单模块视图 — 参考《组织架构模块设计方案.md》第 5.4 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import Menu
from .serializers import MenuSerializer, MenuTreeSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """获取菜单树 — GET /api/menu/tree"""
        menus = Menu.objects.filter(parent__isnull=True).prefetch_related("children")
        return APIResponse.success(data=MenuTreeSerializer(menus, many=True).data)

    @action(detail=False, methods=["get"])
    def options(self, request):
        """获取菜单选项（树形下拉）"""
        return self.tree(request)

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        return APIResponse.success()