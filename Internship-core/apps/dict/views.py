from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import DictType, DictData
from .serializers import DictTypeSerializer, DictDataSerializer


class DictTypeViewSet(viewsets.ModelViewSet):
    queryset = DictType.objects.all()
    serializer_class = DictTypeSerializer
    permission_key = "dict:type:list"
    permission_key_map = {
        "create": "dict:type:add",
        "update": "dict:type:edit",
        "destroy": "dict:type:delete",
        "batch": "dict:type:delete",
        "status": "dict:type:edit",
    }

    def get_permissions(self):
        if self.action in ("list", "retrieve", "by_type"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持按名称筛选
        dict_name = request.query_params.get("dict_name")
        if dict_name:
            queryset = queryset.filter(dict_name__icontains=dict_name)
        dict_type = request.query_params.get("dict_type")
        if dict_type:
            queryset = queryset.filter(dict_type__icontains=dict_type)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

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
        if DictData.objects.filter(dict_type=instance.dict_type).exists():
            return APIResponse.error(message="该字典类型下存在数据项，请先删除数据项")
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        instance = self.get_object()
        status_val = request.data.get("status")
        if status_val not in (0, 1):
            return APIResponse.error(message="状态值无效")
        instance.status = status_val
        instance.save(update_fields=["status", "update_time"])
        return APIResponse.success(message="状态更新成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        # 检查是否有子数据
        types_with_data = DictType.objects.filter(
            id__in=ids,
            dict_type__in=DictData.objects.values_list("dict_type", flat=True).distinct()
        ).values_list("dict_name", flat=True)
        if types_with_data:
            return APIResponse.error(
                message=f"以下字典类型下存在数据项，无法删除：{', '.join(types_with_data)}"
            )
        DictType.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"])
    def export(self, request):
        import csv
        from django.http import HttpResponse
        queryset = DictType.objects.all().order_by("-create_time")
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = (
            f"attachment; filename=dict_types_{timezone.now().strftime('%Y%m%d')}.csv"
        )
        writer = csv.writer(response)
        writer.writerow(["字典名称", "字典类型编码", "状态", "备注", "创建时间"])
        for d in queryset:
            writer.writerow([
                d.dict_name, d.dict_type,
                "启用" if d.status == 1 else "禁用",
                d.remark, d.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        return response


class DictDataViewSet(viewsets.ModelViewSet):
    queryset = DictData.objects.select_related("dict_type").all()
    serializer_class = DictDataSerializer
    permission_key = "dict:data:list"
    permission_key_map = {
        "create": "dict:data:add",
        "update": "dict:data:edit",
        "destroy": "dict:data:delete",
        "batch": "dict:data:delete",
        "status": "dict:data:edit",
    }

    def get_permissions(self):
        if self.action in ("list", "retrieve", "by_type"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), HasPermission()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 按字典类型筛选
        dict_type = request.query_params.get("dict_type")
        if dict_type:
            queryset = queryset.filter(dict_type=dict_type)
        # 按标签筛选
        dict_label = request.query_params.get("dict_label")
        if dict_label:
            queryset = queryset.filter(dict_label__icontains=dict_label)
        # 按状态筛选
        status = request.query_params.get("status")
        if status is not None and status != "":
            try:
                queryset = queryset.filter(status=int(status))
            except (ValueError, TypeError):
                pass
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(data=serializer.data, message="新增成功")

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

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        instance = self.get_object()
        status_val = request.data.get("status")
        if status_val not in (0, 1):
            return APIResponse.error(message="状态值无效")
        instance.status = status_val
        instance.save(update_fields=["status", "update_time"])
        return APIResponse.success(message="状态更新成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        DictData.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"], url_path="type/(?P<dict_type>[^/.]+)")
    def by_type(self, request, dict_type=None):
        """根据字典类型编码获取所有启用的数据项（不分页，用于下拉框）"""
        queryset = DictData.objects.filter(
            dict_type=dict_type, status=1
        ).select_related("dict_type").order_by("sort_order")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
