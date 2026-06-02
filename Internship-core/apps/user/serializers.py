"""用户模块序列化器 — 参考《组织架构模块设计方案.md》第 5.2 节"""
from rest_framework import serializers
from .models import User


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.dept_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "nickname", "email", "telephone",
            "department_name", "status", "create_time",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
