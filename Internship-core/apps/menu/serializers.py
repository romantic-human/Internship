from rest_framework import serializers
from .models import Menu


class MenuSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, default=0)

    class Meta:
        model = Menu
        fields = [
            "id", "parent_id", "menu_name", "menu_type", "path",
            "component", "icon", "permission", "sort_order", "visible",
            "is_frame", "status", "create_time", "update_time",
        ]
        read_only_fields = ["id", "create_time", "update_time"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["parent_id"] = instance.parent_id or 0
        return data


class MenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id", "menu_name", "menu_type", "path",
            "component", "icon", "sort_order", "visible", "is_frame",
            "permission", "status", "children",
        ]

    def get_children(self, obj):
        children = getattr(obj, "_children", [])
        return MenuTreeSerializer(children, many=True).data
