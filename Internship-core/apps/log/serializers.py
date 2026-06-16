"""日志模块序列化器 — 参考《组织架构模块设计方案.md》第 5.7 节"""
from rest_framework import serializers
from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = [
            "id", "username", "module", "operation", "method",
            "request_url", "request_params", "response_result",
            "ip", "status", "execution_time", "create_time",
        ]


class OperationLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = [
            "id", "username", "module", "operation", "method",
            "request_url", "ip", "status", "execution_time", "create_time",
        ]