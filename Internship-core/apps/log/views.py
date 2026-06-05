import openpyxl
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import OperationLog
from .serializers import OperationLogSerializer, OperationLogListSerializer


class OperationLogViewSet(viewsets.ModelViewSet):
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_key = "log:list"
    http_method_names = ["get", "delete", "head", "options"]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def get_serializer_class(self):
        if self.action == "list":
            return OperationLogListSerializer
        return OperationLogSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        username = request.query_params.get("username")
        module = request.query_params.get("module")
        operation = request.query_params.get("operation")
        log_status = request.query_params.get("status")
        start_time = request.query_params.get("startTime") or request.query_params.get("start_date")
        end_time = request.query_params.get("endTime") or request.query_params.get("end_date")

        if username:
            queryset = queryset.filter(username__icontains=username)
        if module:
            queryset = queryset.filter(module__icontains=module)
        if operation:
            queryset = queryset.filter(operation__icontains=operation)
        if log_status is not None:
            queryset = queryset.filter(status=log_status)
        if start_time:
            queryset = queryset.filter(create_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(create_time__lte=end_time)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OperationLogSerializer(instance)
        return APIResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        OperationLog.objects.all().delete()
        return APIResponse.success(message="日志已清空")

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        username = request.query_params.get("username")
        module = request.query_params.get("module")
        operation = request.query_params.get("operation")
        log_status = request.query_params.get("status")
        start_time = request.query_params.get("startTime") or request.query_params.get("start_date")
        end_time = request.query_params.get("endTime") or request.query_params.get("end_date")
        if username:
            queryset = queryset.filter(username__icontains=username)
        if module:
            queryset = queryset.filter(module__icontains=module)
        if operation:
            queryset = queryset.filter(operation__icontains=operation)
        if log_status is not None:
            queryset = queryset.filter(status=log_status)
        if start_time:
            queryset = queryset.filter(create_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(create_time__lte=end_time)
        queryset = queryset[:10000]
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "操作日志"
        headers = ["用户名", "模块", "操作类型", "请求方法", "请求URL", "IP", "状态", "耗时(ms)", "操作时间"]
        ws.append(headers)
        for log in queryset:
            ws.append([
                log.username, log.module, log.operation, log.method,
                log.request_url, log.ip, "成功" if log.status else "失败",
                log.execution_time, log.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="operation_log.xlsx"'
        wb.save(response)
        return response