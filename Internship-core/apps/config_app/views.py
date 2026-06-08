import os
import uuid

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import SystemConfig
from .serializers import SystemConfigSerializer

PANEL_DEFAULTS = {
    "system.name": "企业智能分析平台",
    "system.logo": "",
    "log.enabled": "1",
    "log.retention_days": "90",
    "log.alert_enabled": "1",
    "security.level": "高",
    "security.two_factor": "1",
    "security.password_policy": "至少8位，包含数字与大小写字母",
}


class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_key = "config:list"

    permission_key_map = {
        "batch": "config:delete",
        "panel_save": "config:edit",
    }

    def get_permissions(self):
        if self.action in ("by_key", "panel_get"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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
        serializer.save()
        return APIResponse.success(data=serializer.data, message="更新成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=False, methods=["get"], url_path="by-key")
    def by_key(self, request):
        key = request.query_params.get("key", "")
        if not key:
            return APIResponse.error(message="缺少参数 key")
        config = SystemConfig.objects.filter(config_key=key).first()
        if config:
            return APIResponse.success(data=config.config_value)
        return APIResponse.not_found()

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        instance = self.get_object()
        val = request.data.get("status")
        if val not in (0, 1):
            return APIResponse.error(message="状态值无效")
        instance.status = val
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
        instances = []
        for item in data:
            item_id = item.get("id")
            if not item_id:
                return APIResponse.error(message="每项需要 id 字段")
            instances.append(SystemConfig(id=item_id, sort_order=item.get("sortOrder", 0)))
        SystemConfig.objects.bulk_update(instances, ["sort_order"])
        return APIResponse.success(message="排序更新成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        SystemConfig.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        queryset = SystemConfig.objects.all().order_by("sort_order")
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = f"attachment; filename=configs_{timezone.now().strftime('%Y%m%d')}.csv"
        writer = csv.writer(response)
        writer.writerow(["配置名称", "配置键", "配置值", "类型", "排序", "状态"])
        for c in queryset:
            writer.writerow([c.config_name, c.config_key, c.config_value, c.get_config_type_display(), c.sort_order, c.status])
        return response

    @action(detail=False, methods=["get"], url_path="panel")
    def panel_get(self, request):
        configs = SystemConfig.objects.filter(config_key__in=PANEL_DEFAULTS.keys())
        data = {c.config_key: c.config_value for c in configs}
        for key, default in PANEL_DEFAULTS.items():
            if key not in data:
                data[key] = default
        return APIResponse.success(data=data)

    @action(detail=False, methods=["post"], url_path="panel-save")
    def panel_save(self, request):
        payload = request.data
        for key, value in payload.items():
            if key not in PANEL_DEFAULTS:
                continue
            obj, created = SystemConfig.objects.get_or_create(
                config_key=key,
                defaults={"config_name": key, "config_value": str(value), "config_type": 0, "status": 1},
            )
            if not created:
                obj.config_value = str(value)
                obj.save(update_fields=["config_value", "update_time"])
        return APIResponse.success(message="配置保存成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_image(request):
    file = request.FILES.get("file")
    if not file:
        return APIResponse.error(message="请选择文件", code=2000, http_status=400)
    if file.size > 2 * 1024 * 1024:
        return APIResponse.error(message="文件大小不能超过 2MB", code=2000, http_status=400)
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"):
        return APIResponse.error(message="不支持的格式", code=2000, http_status=400)
    upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        for chunk in file.chunks():
            f.write(chunk)
    url = f"{settings.MEDIA_URL}uploads/{filename}"
    return APIResponse.success(message="上传成功", data={"url": url})
