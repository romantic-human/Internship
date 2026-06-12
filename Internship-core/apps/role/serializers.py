"""角色模块序列化器 — 参考《组织架构模块设计方案.md》第 5.3 节"""
from rest_framework import serializers
from .models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "role_name", "role_key", "role_sort", "status", "remark", "create_time", "update_time"]


class AssignMenuSerializer(serializers.Serializer):
    menu_ids = serializers.ListField(child=serializers.IntegerField())


class AssignUserSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())