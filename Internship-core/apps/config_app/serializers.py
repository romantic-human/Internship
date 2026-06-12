"""系统配置模块序列化器 — 参考《组织架构模块设计方案.md》第 5.8 节"""
from rest_framework import serializers
from .models import SystemConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            "id", "config_name", "config_key", "config_value", "config_type",
            "remark", "status", "sort_order", "create_time", "update_time",
        ]