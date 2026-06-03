from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, default=0)

    class Meta:
        model = Department
        fields = [
            "id", "parent_id", "dept_name", "leader", "phone", "email",
            "sort_order", "status", "create_time", "update_time",
        ]
        read_only_fields = ["id", "create_time", "update_time"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["parent_id"] = instance.parent_id or 0
        return data


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id", "dept_name", "leader", "phone", "email",
            "sort_order", "status", "children",
        ]

    def get_children(self, obj):
        children = Department.objects.filter(parent=obj).order_by("sort_order")
        return DepartmentTreeSerializer(children, many=True).data
