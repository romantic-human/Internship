from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import Menu
from .serializers import MenuSerializer, MenuTreeSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_key = "menu:list"

    def get_permissions(self):
        if self.action in ("tree", "options"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def get_queryset(self):
        qs = super().get_queryset()
        menu_name = self.request.query_params.get("menu_name")
        if menu_name:
            qs = qs.filter(menu_name__icontains=menu_name)
        return qs

    def perform_create(self, serializer):
        parent_id = serializer.validated_data.pop("parent_id", 0)
        if parent_id:
            serializer.save(parent_id=parent_id)
        else:
            serializer.save(parent=None)

    def perform_update(self, serializer):
        parent_id = serializer.validated_data.pop("parent_id", None)
        if parent_id is not None:
            if parent_id:
                serializer.save(parent_id=parent_id)
            else:
                serializer.save(parent=None)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(data=serializer.data, message="新增成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if Menu.objects.filter(parent=instance).exists():
            return APIResponse.error(message="存在子菜单，无法删除")
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        menu_name = request.query_params.get("menu_name", "")
        qs = Menu.objects.all()
        if menu_name:
            qs = qs.filter(menu_name__icontains=menu_name)
        all_menus = list(qs.order_by("sort_order"))
        parent_map = {}
        for m in all_menus:
            m._children = []
            parent_map[m.id] = m
        roots = []
        for m in all_menus:
            if m.parent_id and m.parent_id in parent_map:
                parent_map[m.parent_id]._children.append(m)
            else:
                roots.append(m)
        return APIResponse.success(data=MenuTreeSerializer(roots, many=True).data)

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        return self.tree(request)

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        instance = self.get_object()
        status_val = request.data.get("status")
        if status_val not in (0, 1):
            return APIResponse.error(message="状态值无效")
        instance.status = status_val
        instance.save()
        return APIResponse.success(message="状态更新成功")

    @action(detail=True, methods=["put"], url_path="sort")
    def sort(self, request, pk=None):
        instance = self.get_object()
        sort_order = request.data.get("sortOrder", 0)
        instance.sort_order = sort_order
        instance.save()
        return APIResponse.success(message="排序更新成功")

    @action(detail=False, methods=["post"], url_path="batch-sort")
    def batch_sort(self, request):
        data = request.data
        if not isinstance(data, list):
            return APIResponse.error(message="请传入数组")
        instances = []
        for item in data:
            item_id = item.get("id")
            if not item_id:
                return APIResponse.error(message="每项需要 id 字段")
            instances.append(Menu(id=item_id, sort_order=item.get("sortOrder", 0)))
        Menu.objects.bulk_update(instances, ["sort_order"])
        return APIResponse.success(message="排序更新成功")