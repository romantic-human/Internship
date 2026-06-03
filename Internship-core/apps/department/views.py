"""部门模块视图 — 参考《组织架构模块设计方案.md》第 5.6 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import Department
from .serializers import DepartmentSerializer, DepartmentTreeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @action(detail=False, methods=["get"])
    def tree(self, request):
        """获取部门树 — GET /api/department/tree"""
        depts = Department.objects.filter(parent__isnull=True).prefetch_related("children")
        return APIResponse.success(data=DepartmentTreeSerializer(depts, many=True).data)

    @action(detail=True, methods=["put"])
    def status(self, request, pk=None):
        """修改状态 — PUT /api/department/:id/status"""
        dept = self.get_object()
        dept.status = request.data.get("status", dept.status)
        dept.save(update_fields=["status"])
        return APIResponse.success(message="状态更新成功")

    @action(detail=True, methods=["put"])
    def sort(self, request, pk=None):
        """更新排序 — PUT /api/department/:id/sort"""
        dept = self.get_object()
        dept.sort_order = request.data.get("sortOrder", dept.sort_order)
        dept.save(update_fields=["sort_order"])
        return APIResponse.success(message="排序更新成功")

    @action(detail=False, methods=["post"])
    def batch_sort(self, request):
        """批量排序 — POST /api/department/batch-sort"""
        items = request.data
        if not isinstance(items, list):
            return APIResponse.error(message="参数格式错误：应为数组", code=2000)
        for item in items:
            Department.objects.filter(id=item.get("id")).update(sort_order=item.get("sortOrder", 0))
        return APIResponse.success(message="批量排序成功")