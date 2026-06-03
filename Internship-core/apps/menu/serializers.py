"""菜单模块序列化器 — 参考《组织架构模块设计方案.md》第 5.4 节"""
from rest_framework import serializers
from .models import Menu


class MenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id", "parent", "menu_name", "menu_type", "path",
            "component", "icon", "sort_order", "visible", "status", "children",
        ]

    def get_children(self, obj):
        if hasattr(obj, "children"):
            return MenuTreeSerializer(obj.children.all(), many=True).data
        return []


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"