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
        return APIResponse.success()