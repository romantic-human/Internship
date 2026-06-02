"""权限模块序列化器 — 参考《组织架构模块设计方案.md》第 5.5 节"""
from rest_framework import serializers
from .models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"
