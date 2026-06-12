from rest_framework import serializers
from .models import DictType, DictData


class DictTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DictType
        fields = [
            "id", "dict_name", "dict_type", "status", "remark",
            "create_time", "update_time",
        ]
        read_only_fields = ["id", "create_time", "update_time"]


class DictDataSerializer(serializers.ModelSerializer):
    # 返回时附带字典类型名称
    dict_type_name = serializers.CharField(source="dict_type.dict_name", read_only=True)

    class Meta:
        model = DictData
        fields = [
            "id", "dict_type", "dict_type_name",
            "dict_label", "dict_value", "css_class", "list_class",
            "sort_order", "status", "is_default", "remark",
            "create_time", "update_time",
        ]
        read_only_fields = ["id", "create_time", "update_time"]
