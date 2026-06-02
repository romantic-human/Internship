"""日志模块视图 — 参考《组织架构模块设计方案.md》第 5.7 节"""
from rest_framework import viewsets
from rest_framework.decorators import action
from utils import APIResponse
from .models import OperationLog
from .serializers import OperationLogSerializer, OperationLogListSerializer


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """日志只有查询和清空功能"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OperationLogListSerializer
        return OperationLogSerializer

    def destroy(self, request, *args, **kwargs):
        """清空日志 — DELETE /api/log"""
        return APIResponse.success(data={"message": "待实现"})

    @action(detail=False, methods=["get"])
    def export(self, request):
        """导出日志 — GET /api/log/export"""
        return APIResponse.success(data={"message": "待实现"})
