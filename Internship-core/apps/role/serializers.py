"""角色模块序列化器 — 参考《组织架构模块设计方案.md》第 5.3 节"""
from rest_framework import serializers
from .models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class AssignMenuSerializer(serializers.Serializer):
    menu_ids = serializers.ListField(child=serializers.IntegerField())


class AssignUserSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())
