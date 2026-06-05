from django.db import transaction
import csv
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import Permission, MenuPermissionRelation
from .serializers import PermissionSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_key = "permission:list"

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get("permission_name")
        status_val = self.request.query_params.get("status")
        if name:
            qs = qs.filter(permission_name__icontains=name)
        if status_val is not None and status_val != "":
            qs = qs.filter(status=status_val)
        return qs

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

    @action(detail=True, methods=["get", "put"], url_path="menus")
    def menus(self, request, pk=None):
        instance = self.get_object()
        if request.method == "GET":
            menu_ids = MenuPermissionRelation.objects.filter(
                permission=instance
            ).values_list("menu_id", flat=True)
            return APIResponse.success(data=list(menu_ids))
        menu_ids = request.data.get("menuIds", [])
        with transaction.atomic():
            MenuPermissionRelation.objects.filter(permission=instance).delete()
            if menu_ids:
                relations = [MenuPermissionRelation(permission=instance, menu_id=mid) for mid in menu_ids]
                MenuPermissionRelation.objects.bulk_create(relations)
        return APIResponse.success(message="绑定成功")

    @action(detail=False, methods=["delete"], url_path="batch")
    def batch(self, request):
        """批量删除 — DELETE /api/permission/batch"""
        ids = request.data.get("ids", [])
        if not ids:
            return APIResponse.error(message="ids 不能为空")
        Permission.objects.filter(id__in=ids).delete()
        return APIResponse.success(message="批量删除成功")

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """导出权限 — GET /api/permission/export"""
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="permissions.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "权限名称", "权限标识", "排序", "状态", "创建时间"])
        perms = self.get_queryset().order_by("sort_order")
        for p in perms:
            writer.writerow([p.id, p.permission_name, p.permission_key, p.sort_order, "启用" if p.status else "禁用", p.create_time])
        return response

    @action(detail=True, methods=["put"], url_path="status")
    def status(self, request, pk=None):
        """状态切换 — PUT /api/permission/<id>/status"""
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
        instances = []
        for item in data:
            item_id = item.get("id")
            if not item_id:
                return APIResponse.error(message="每项需要 id 字段")
            instances.append(Permission(id=item_id, sort_order=item.get("sortOrder", 0)))
        Permission.objects.bulk_update(instances, ["sort_order"])
        return APIResponse.success(message="排序更新成功")