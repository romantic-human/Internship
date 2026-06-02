"""部门模块序列化器 — 参考《组织架构模块设计方案.md》第 5.6 节"""
from rest_framework import serializers
from .models import Department


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ["id", "parent", "dept_name", "leader", "sort_order", "status", "children"]

    def get_children(self, obj):
        if hasattr(obj, "children"):
            return DepartmentTreeSerializer(obj.children.all(), many=True).data
        return []


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
