from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import Department
from .serializers import DepartmentSerializer, DepartmentTreeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_key = "dept:list"

    def get_permissions(self):
        if self.action == "tree":
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

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
        if Department.objects.filter(parent=instance).exists():
            return APIResponse.error(message="存在子部门，无法删除")
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        depts = Department.objects.filter(parent__isnull=True).order_by("sort_order")
        return APIResponse.success(data=DepartmentTreeSerializer(depts, many=True).data)

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
        instance.sort_order = request.data.get("sortOrder", 0)
        instance.save()
        return APIResponse.success(message="排序更新成功")

    @action(detail=False, methods=["post"], url_path="batch-sort")
    def batch_sort(self, request):
        data = request.data
        if not isinstance(data, list):
            return APIResponse.error(message="请传入数组")
        instances = [Department(id=item["id"], sort_order=item.get("sortOrder", 0)) for item in data]
        Department.objects.bulk_update(instances, ["sort_order"])
        return APIResponse.success(message="排序更新成功")
