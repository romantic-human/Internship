"""系统配置模块序列化器 — 参考《组织架构模块设计方案.md》第 5.8 节"""
from rest_framework import serializers
from .models import SystemConfig, AIModelConfig


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            "id", "config_name", "config_key", "config_value", "config_type",
            "remark", "status", "sort_order", "create_time", "update_time",
        ]


class AIModelConfigSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source="get_provider_display", read_only=True)
    model_type_display = serializers.CharField(source="get_model_type_display", read_only=True)

    class Meta:
        model = AIModelConfig
        fields = [
            "id", "name", "provider", "provider_display",
            "model_type", "model_type_display", "model_name",
            "api_key", "api_base_url", "is_default",
            "status", "remark", "create_time", "update_time",
        ]
        read_only_fields = ["id", "create_time", "update_time"]

    def validate_api_key(self, value):
        """API Key 不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("API Key 不能为空")
        return value.strip()

    def validate_api_base_url(self, value):
        """API 地址不能为空"""
        if not value or not value.strip():
            raise serializers.ValidationError("API 地址不能为空")
        return value.strip().rstrip("/")