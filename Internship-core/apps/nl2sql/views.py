"""NL2SQL 分析视图"""
import logging
import time

from django.db import transaction
from rest_framework import viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from utils.response import APIResponse
from utils.permissions import HasPermission
from .models import DataSource, QueryHistory
from .serializers import (
    DataSourceSerializer, QueryHistorySerializer,
    QueryRequestSerializer, DbConnectionTestSerializer,
)
from .services.db_service import get_tables_and_columns, build_schema_ddl, test_connection
from .services.nl2sql_service import NL2SQLService
from .services.sql_executor import execute_sql

logger = logging.getLogger(__name__)


class DataSourceViewSet(viewsets.ModelViewSet):
    """数据源 CRUD"""
    queryset = DataSource.objects.select_related("created_by").all()
    serializer_class = DataSourceSerializer
    permission_key = "nl2sql:list"
    permission_key_map = {
        "create": "nl2sql:add",
        "update": "nl2sql:edit",
        "destroy": "nl2sql:delete",
        "tables": "nl2sql:list",
        "test_conn": "nl2sql:list",
    }

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return APIResponse.success(data=serializer.data, message="新增成功")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        name = request.query_params.get("name", "").strip()
        if name:
            queryset = queryset.filter(name__icontains=name)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
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

    @action(detail=True, methods=["get"], url_path="tables")
    def tables(self, request, pk=None):
        """获取数据源的表结构"""
        instance = self.get_object()
        try:
            meta = get_tables_and_columns(
                db_type=instance.db_type,
                host=instance.host,
                port=instance.port,
                db_name=instance.db_name,
                username=instance.username,
                password=instance.get_password(),
            )
            return APIResponse.success(data=meta)
        except Exception as e:
            return APIResponse.error(message=f"获取表结构失败: {str(e)}", code=5000, http_status=500)

    @action(detail=True, methods=["post"], url_path="test")
    def test_conn(self, request, pk=None):
        """测试数据源连接"""
        instance = self.get_object()
        success, msg = test_connection(
            db_type=instance.db_type,
            host=instance.host,
            port=instance.port,
            db_name=instance.db_name,
            username=instance.username,
            password=instance.get_password(),
        )
        if success:
            return APIResponse.success(message=msg)
        return APIResponse.error(message=msg, code=5000, http_status=500)


class QueryHistoryViewSet(viewsets.GenericViewSet):
    """查询历史"""
    queryset = QueryHistory.objects.select_related("user", "datasource").all()
    serializer_class = QueryHistorySerializer
    permission_key = "nl2sql:list"
    permission_key_map = {
        "destroy": "nl2sql:delete",
        "favorite": "nl2sql:edit",
    }

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user=request.user)
        datasource_id = request.query_params.get("datasource_id")
        is_favorite = request.query_params.get("is_favorite")
        if datasource_id:
            queryset = queryset.filter(datasource_id=datasource_id)
        if is_favorite:
            queryset = queryset.filter(is_favorite=1)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_superuser:
            return APIResponse.error(message="无权删除他人记录", code=3003, http_status=403)
        instance.delete()
        return APIResponse.success(message="删除成功")

    @action(detail=True, methods=["put"], url_path="favorite")
    def favorite(self, request, pk=None):
        """收藏/取消收藏"""
        instance = self.get_object()
        if instance.user != request.user and not request.user.is_superuser:
            return APIResponse.error(message="无权操作他人记录", code=3003, http_status=403)
        instance.is_favorite = 1 if not instance.is_favorite else 0
        instance.save(update_fields=["is_favorite"])
        return APIResponse.success(data={"is_favorite": instance.is_favorite}, message="操作成功")


class QueryView(APIView):
    """NL2SQL 核心查询接口"""
    permission_classes = [IsAuthenticated, HasPermission]
    permission_key = "nl2sql:query"

    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        datasource_id = serializer.validated_data["datasource_id"]
        question = serializer.validated_data["question"]

        try:
            ds = DataSource.objects.get(id=datasource_id, status=1)
        except DataSource.DoesNotExist:
            return APIResponse.error(message="数据源不存在或已禁用", code=2004, http_status=404)

        start_time = time.time()
        try:
            meta = get_tables_and_columns(
                db_type=ds.db_type, host=ds.host, port=ds.port,
                db_name=ds.db_name, username=ds.username,
                password=ds.get_password(),
            )
            schema_ddl = build_schema_ddl(meta)
            generated_sql = NL2SQLService.generate_sql(schema_ddl, question)
            result = execute_sql(
                host=ds.host, port=ds.port, db_name=ds.db_name,
                username=ds.username, password=ds.get_password(),
                sql=generated_sql,
            )
            elapsed = round(time.time() - start_time, 3)

            with transaction.atomic():
                QueryHistory.objects.create(
                    user=request.user,
                    datasource=ds,
                    question=question,
                    generated_sql=generated_sql,
                    execution_time=elapsed,
                    result_count=result.get("row_count", 0),
                    status=1 if "error" not in result else 0,
                    error_message=result.get("error", ""),
                )

            if "error" in result:
                return APIResponse.error(message=result["error"], code=5000, http_status=500)

            return APIResponse.success(data={
                "sql": generated_sql,
                "columns": result.get("columns", []),
                "rows": result.get("rows", []),
                "row_count": result.get("row_count", 0),
                "execution_time": elapsed,
            })
        except Exception as e:
            logger.exception("NL2SQL 查询失败")
            elapsed = round(time.time() - start_time, 3)
            QueryHistory.objects.create(
                user=request.user,
                datasource=ds,
                question=question,
                generated_sql="",
                execution_time=elapsed,
                result_count=0,
                status=0,
                error_message=str(e),
            )
            return APIResponse.error(message=f"查询失败: {str(e)}", code=5000, http_status=500)
